#!/usr/bin/env python

import re
import sys


def tokenizeDoc(cur_doc):
    return re.findall('\\w+', cur_doc)

# with open("abstract.tiny.train") as f:
#     for line in f:


for line in sys.stdin:
    contents = re.split(r'\t', line)
    # print len(contents)
    labels = contents[1].split(",")
    document = tokenizeDoc(contents[2])
    for label in labels:
        # if label.endswith("CAT"):
        print("Y=*\t1")
        print("Y=" + label + "\t1")
        # Check if word occurs in the document
        for words in document:
            # wDkey = label + '~' + words
            print("Y=" + label + ",W=" + words + "\t1")
            print("Y=" + label + ",W=*\t1")
