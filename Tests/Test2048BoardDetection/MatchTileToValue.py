import cv2
import os
import json
import numpy as np
import Game2048ImageProc

# def correlateImage(imgIn, tileDefs):
#     tilePath = "../TestOutputs/Tiles/"
#     imgInGray = cv2.cvtColor(imgIn, cv2.COLOR_BGR2GRAY)
#     for key in tileDefs["fnameToValue"]:
#
#         tile = cv2.imread(tilePath+key, cv2.CV_LOAD_IMAGE_GRAYSCALE)
#         if tile is None:
#             print("Can't open " + key)
#             return False
#
#         w, h = tile.shape[::-1]
#
#         # Apply template Matching
#         method = cv2.TM_CCOEFF_NORMED
#         res = cv2.matchTemplate(imgInGray, tile, method)
#         threshold = 0.7
#         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#         if max_val > threshold:
#             print("Found something " + key + " value " + tileDefs["fnameToValue"][key])
#
#     meanAndStdDev = cv2.meanStdDev(imgIn)
#     print(meanAndStdDev)


    #         sq, sqValid = identifySq(pt, w, h)
    #         if sqValid:
    #             candidatesFound.append([sq, tileVal, res])
    #     tileVal *= 2
    #
    # candidatesFound.sort(key=lambda cand: cand[0])
    # posVals = []
    # curSq = 0
    # for cand in candidatesFound:
    #     sq = cand[0]
    #     tileVal = cand[1]
    #     if sq != curSq:
    #         posVals.sort(key=lambda pos: pos[1])
    #         if len(posVals) > 0 and posVals[len(posVals) - 1] != 0:
    #             boardCells[curSq] = posVals[len(posVals) - 1][0]
    #         posVals = []
    #         curSq = sq
    #     else:
    #         foundVal = False
    #         for posVal in posVals:
    #             if tileVal == posVal[0]:
    #                 posVal[1] += 1
    #                 foundVal = True
    #         if not foundVal:
    #             posVals.append([tileVal, 1])
    # posVals.sort(key=lambda pos: pos[1])
    # if len(posVals) > 0 and posVals[len(posVals) - 1] != 0:
    #     boardCells[curSq] = posVals[len(posVals) - 1][0]

tileBasePath = "../TestOutputs/Tiles/"
jsonMapFileName = "../TestOutputs/Tiles/tileDefs.json"

tileDefs = { "fnameToValue": {} }
with open(jsonMapFileName, "r") as jsonFile:
    tileDefs = json.load(jsonFile)

if not "fnameToValue" in tileDefs:
    print("Can't get tile defs")
    exit(0)

tileImgsAndValues = []
for fname in tileDefs["fnameToValue"]:
    tileImg = cv2.imread(tileBasePath + fname, cv2.CV_LOAD_IMAGE_GRAYSCALE)
    if tileImg is None:
        print("Can't open tile image " + fname)
    tileImgsAndValues.append({ "img": tileImg, "value": tileDefs["fnameToValue"][fname]})

for subdir, dirs, files in os.walk("../TestImgs"):
    for fil in files:
        filepath = subdir + os.sep + fil
        if not filepath.endswith("1280.jpg"):
            continue
        img = cv2.imread(fname)
        rslt, imOut = Game2048ImageProc.extractGameBoard(img)
        if not rslt:
            print(".... in Image " + filepath)
            continue
        print("Testing " + fil)
        imgTiles = Game2048ImageProc.extractTilesFromImage(imOut, 5)
        fileBase, fileExt = os.path.splitext(fil)
        for imgIdx in range(len(imgTiles)):
            # correlateImage(imgTiles[imgIdx], tileDefs)
            tileVal = Game2048ImageProc.getTileValue(imgTiles[imgIdx], tileImgsAndValues)
            print("Tile value found = ", tileVal)
            cv2.imshow("tile", imgTiles[imgIdx])
            keyPress = cv2.waitKey(0)
            if keyPress == 27:
                exit(0)

