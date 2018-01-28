from guineapig import *
import sys
import math
# supporting routines can go here

# always subclass Planner
def tokens((docid,labels,words)):
    for label in labels:
    	for word in words:
    		yield (docid, label, word)
def testForm((docid, words)):
    yield ('*', "~ctr---"+docid)
    for word in words:
		yield (word, "~ctr---"+docid)
def testFlatten(row):
    yield(row[1])
def classify(row):
    labels=set()
    wordDocument=dict()
    labelDict=dict()
    words=list()
    result=dict()
    # yield row[1]
    # yield row[1][0]
    # yield row[0][1]
    modV = row[2]
    addLabels = False
    # yield modV
    for wordRow in row[1]:
        if wordRow[0] == '*':
            addLabels = True
        else:
            words.append(wordRow[0])
        if wordRow[1] is not None:
            #yield wordRow[1][1] #[('Agent', 8, 135, 2589), ('Event', 2, 34, 2589), ('MeanOfTransportation', 4, 30, 2589), ('Organisation', 2, 138, 2589), ('Person', 51, 849, 2589), ('Place', 19, 540, 2589), ('Species', 3, 226, 2589), ('Work', 9, 274, 2589), ('other', 12, 289, 2589)]
            for element in wordRow[1][1]:
                wordDocument[element[0],wordRow[1][0]] = element[1]
                labelDict[element[0]] = element[2]
                labelDict['yTotal'] = element[3]
                if addLabels:
                    labels.add(element[0])
            addLabels = False

    for word in words:
        # yield word
        for label in labels:
            #yield label
            result[label]=result.setdefault(label,math.log(float(labelDict[label])/labelDict['yTotal']))+math.log(((1.0/modV)+wordDocument.setdefault((label,word),0))/(wordDocument[(label,'*')]+1.0))
    #     yield wordRow
    # yield result
    maxVal = float(-sys.maxint-1)
    total = 0.0
    predicted = None
    for key,value in result.items():
        total += value
        if value > maxVal:
            maxVal = value
            predicted = key
    yield (row[0][7:], predicted, float(maxVal)*100/total)
class NB(Planner):
    # params is a dictionary of params given on the command line.
    #  e.g. trainFile = params['trainFile']
    params = GPig.getArgvParams()
    # lines = ReadLines(sys.argv[1])
    # lines = ReadLines(params['corpus'])
    data = ReadLines(params['trainFile']) \
    | ReplaceEach(by=lambda line:line.strip().split("\t")) \
    | ReplaceEach(by=lambda(docid,labels,str): (docid,labels.split(","),str.lower().split())) \
    | Flatten(by=tokens)
    # wordCount = Group(words, by=lambda x: x, reducingTo=ReduceToCount())
    #Vocabulary
    vocab = ReplaceEach(data, by=lambda(docid,label,term):(term)) | Distinct() \
    | Group(by=lambda(term):term, reducingTo=ReduceToCount()) \
    | ReplaceEach(by=lambda(label,count):count) \
    | Group(by=lambda count:'vocab', reducingTo=ReduceToSum()) \
    | ReplaceEach(by=lambda(totalVocab,count):count)
    #C["Y=y & W=wj"]
    docFreq = Group(data, by=lambda(docid,label,term):(label,term), reducingTo=ReduceToCount()) | ReplaceEach(by=lambda((label,term),df):(label,term,df))
    #C["Y=y & W=any"]
    docANY = Group(docFreq, by=lambda (label,term,df):label, reducingTo=ReduceToCount()) | ReplaceEach(by=lambda(label,count):(label,'*',count))
    #C["Y=y & W=wj"]+C["Y=y & W=any"]
    docTotals = Union(docFreq, docANY)
    # C["Y=y"]
    nlabels = ReplaceEach(data, by=lambda(docid,label,term):(docid,label)) \
    | Distinct() \
    | Group(by=lambda(docid,label):label, reducingTo=ReduceToCount())
    # C["Y=any"]
    yANY = ReplaceEach(nlabels,by=lambda(label,count):count) | Group(by=lambda count:'y*', reducingTo=ReduceToSum()) | ReplaceEach(by=lambda(totalY,count):count)
    # C["Y=y"] + ["Y=any"]
    labelsTotal = Union(yANY, nlabels)
    
    wordVector = Join(Jin(docTotals, by=lambda(label,word,count):label), Jin(nlabels, by=lambda(label, count):label)) \
    | ReplaceEach(by=lambda((label1,term,df),(label2,ctr)):(label1,term,df,ctr)) \
    | Augment(sideview=yANY, loadedBy=lambda v:GPig.onlyRowOf(v)) \
    | ReplaceEach(by=lambda((label,word,wordTotal,labelTotal),count):(label,word,wordTotal,labelTotal,count)) \
    | Group(by=lambda(label,word,wordTotal,labelTotal,count):word, retaining=lambda(label,word,wordTotal,labelTotal,count):(label,wordTotal,labelTotal,count))

    # wordVectorTotal = Augment(wordVector, sideview=labelsTotal, loadedBy=lambda v:GPig.onlyRowOf(v))
    #test
    testData = ReadLines(params['testFile']) \
    | ReplaceEach(by=lambda line:line.strip().split("\t")) \
    | ReplaceEach(by=lambda(docid,labels,str): (docid, str.lower().split())) \
    | Flatten(by=testForm)
    #Join format: (word, (C[w^Y=...],C[w^Y=...]), request)
    # joinTest = Join(Jin(wordVector, by=lambda (word, row):word), Jin(testData, by=lambda (word, row):word, outer=True)) | ReplaceEach(by=lambda((row1),(word2,ctr)):(row1,ctr))#| ReplaceEach(by=lambda((word1,row),(word2,ctr)):(word1,row,ctr))
    joinTest = Join(Jin(wordVector, by=lambda (word, row):word), Jin(testData, by=lambda (word, row):word, outer=True)) \
    | ReplaceEach(by=lambda((row1),(word2,ctr)):(word2,row1,ctr))#| ReplaceEach(by=lambda((word1,row),(word2,ctr)):(word1,row,ctr))
    # groupRequest = Group(joinTest, by=lambda(word1,row,ctr):ctr, retaining=lambda(word1,row,ctr):(word1,row))
    # groupRequest = Group(joinTest, by=lambda(row1,ctr):ctr, retaining=lambda(row1, ctr):row1)
    output = Group(joinTest, by=lambda(word2,row1,ctr):ctr, retaining=lambda(word2,row1,ctr):(word2, row1)) \
    | Augment(sideview=vocab, loadedBy=lambda v:GPig.onlyRowOf(v)) \
    | ReplaceEach(by=lambda((word2,row),count):(word2,row,count)) \
    | Flatten(by=classify)

# always end like this
if __name__ == "__main__":
    NB().main(sys.argv)

# supporting routines can go here
