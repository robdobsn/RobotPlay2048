
import cv2
import Game2048ImageProc

import os
for subdir, dirs, files in os.walk("../TestImgs/Free"):
    for fil in files:
        # print os.path.join(subdir, fil)
        filepath = subdir + os.sep + fil
        if not filepath.endswith("1280.jpg"):
            continue
        img = cv2.imread(fname)
        rslt, imOut = Game2048ImageProc.extractGameBoard(img)
        if not rslt:
            print(".... in Image " + filepath)
            continue
        imgTiles = Game2048ImageProc.extractTilesFromImage(imOut)
        fileBase, fileExt = os.path.splitext(fil)
        for imgIdx in range(len(imgTiles)):
            fileoutname = "../TestOutputs/Tiles" + os.sep + fileBase + "_" + str(imgIdx) + fileExt
            imgCrop = imgTiles[imgIdx]
            xSize = imgCrop.shape[1]
            ySize = imgCrop.shape[0]
            imgCrop = imgCrop[5:ySize-5,5:xSize-5]
            cv2.imwrite(fileoutname, imgCrop)


