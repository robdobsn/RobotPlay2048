
import cv2
import GameImageHandler

def testImage(fname):

    # Open image and resize
    img = cv2.imread(fname)
    resizedImg = cv2.resize(img, (640, int(640*img.shape[0]/img.shape[1])), interpolation=cv2.INTER_CUBIC)
    imgDbg = resizedImg.copy()
    xRes = resizedImg.shape[1]
    yRes = resizedImg.shape[0]
    # print("xRes", xRes, "yRes", yRes)

    # Find lines in image
    candLines = GameImageHandler.findLinesInImage(resizedImg)
    if len(candLines) < 4:
        print("Not enough lines to find a rectangle")
        return False, None

    # Find the smallest large-enough rectangle close to the centre of the image
    rectSides = GameImageHandler.findRectangleAroundPoint(candLines, (xRes / 2, yRes / 2), xRes / 4)

    # Check we found a valid rect
    for side in rectSides:
        if not side:
            print("One or more sides of the rectangle can't be found")
            return False, None

    # Find corners of rectangle
    cornerPts = GameImageHandler.findRectangleCorners(rectSides)
    if len(cornerPts) != 4:
        print("Not enough corners found")
        return False, None

    # Rearrange the corners so the top left corner is first and corners are clockwise
    corners = GameImageHandler.normalizeCorners(cornerPts)

    # Warp the image back to right rectangle
    im_out = GameImageHandler.warpImageToRightRect(resizedImg, corners, 300, 5)

    return True, im_out

    # # Split image into 16 cells
    # imOutXRes = im_out.shape[1]
    # imOutYRes = im_out.shape[0]
    # xCells = 4
    # yCells = 4
    # imgCells = []
    # for yIdx in range(yCells):
    #     for xIdx in range(xCells):
    #         tlx = xIdx * imOutXRes / xCells
    #         tly = yIdx * imOutYRes / yCells
    #         wid = imOutXRes / xCells
    #         hig = imOutYRes / yCells
    #         cellImg = im_out[tly:tly + hig, tlx:tlx + wid]
    #         imgCells.append(cellImg)


import os
for subdir, dirs, files in os.walk("../TestImgs/Free"):
    for fil in files:
        # print os.path.join(subdir, fil)
        filepath = subdir + os.sep + fil
        if filepath.endswith(".jpg"):
            rslt, imOut = testImage(filepath)
            if not rslt:
                print(".... in Image " + filepath)
            else:
                fileoutname = "../TestOutputs/Imgs" + os.sep + fil
                fileoutname = fileoutname.replace(".jpg", "munged.jpg")
                cv2.imwrite(fileoutname, imOut)

