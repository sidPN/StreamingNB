#!/usr/bin/env python

import re
import sys
import math

previousKey = None
sumForPreviousKey = 0

# def outputPreviousKey(previousKey, sumForPreviousKey):
#     if previousKey is not None:
#         print(previousKey + "\t" + str(sumForPreviousKey))

# with open("test") as f:
for line in sys.stdin:
# for line in f:
    # print(line)
    line.strip()
    keyValue = re.split(r'\t+', line)
    if keyValue[0] == previousKey:
        sumForPreviousKey += 1
        # print(sumForPreviousKey)
    else:
        # outputPreviousKey(previousKey, sumForPreviousKey)
        if previousKey is not None:
            print(previousKey + "\t" + str(sumForPreviousKey))
        previousKey = keyValue[0]
        sumForPreviousKey = 1
# outputPreviousKey(previousKey, sumForPreviousKey)
# print(previousKey + "\t" + str(sumForPreviousKey))
if previousKey == keyValue[0]:
    print(previousKey + "\t" + str(sumForPreviousKey))