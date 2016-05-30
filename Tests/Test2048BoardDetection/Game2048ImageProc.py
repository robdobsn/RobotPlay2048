import cv2
import numpy as np
import GameImageHandler
import GameGeometry
import json

def extractGameBoard(img):
#    return extractGameBoardUsingLines(img)
    return extractGameBoardUsingContours(img)

def extractGameBoardUsingContours(img):

    # Open image and resize
    resizedImg = cv2.resize(img, (640, int(640*img.shape[0]/img.shape[1])), interpolation=cv2.INTER_CUBIC)
    imgDbg = resizedImg.copy()
    xRes = resizedImg.shape[1]
    yRes = resizedImg.shape[0]

    # Work out a reasonable perimiter - assumes the game area occupies around 50% of the
    # minimum dimension of the image
    MIN_CONTOUR_PERIM = min(xRes, yRes) * 0.5 * 4 * 0.6
    MAX_CONTOUR_PERIM = min(xRes, yRes) * 0.5 * 4 * 1.5
    print("Min/Max", MIN_CONTOUR_PERIM, MAX_CONTOUR_PERIM)
    WORST_SQUARE_FACTOR = 0.2

    # Find contours
    imgray = cv2.cvtColor(resizedImg, cv2.COLOR_BGR2GRAY)
    thresh = cv2.Canny(imgray, 50, 200, apertureSize=3)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    closestToSquareCorners = []
    closestToSquareFactor = 10000

    # loop over contours
    print("Num contours found", len(contours))
    for contour in contours:
        # approximate the contour
        perim = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perim, True)

        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:
            if MIN_CONTOUR_PERIM <= perim <= MAX_CONTOUR_PERIM:

                # Corners of contour
                corners = []
                for corner in approx:
                    corners.append(corner[0])

                # Rearrange the corners so the top left corner is first and corners are clockwise
                corners = GameImageHandler.normalizeCorners(corners)

                # See if it is the best approximation to a square
                side1Len = GameGeometry.distPtToPt(corners[0], corners[1])
                side2Len = GameGeometry.distPtToPt(corners[1], corners[2])
                squareFactor = abs(side1Len - side2Len) / min(xRes, yRes)

                print(abs(side1Len - side2Len), side1Len, squareFactor)

                if closestToSquareFactor > squareFactor and squareFactor < WORST_SQUARE_FACTOR:
                    closestToSquareFactor = squareFactor
                    closestToSquareCorners = corners


    # # Debug
    # print("Most square found", perim, closestToSquareCorners)
    # if len(closestToSquareCorners) == 4:
    #     debugPlayAreaContours = []
    #     debugPlayAreaContours.append(closestToSquareCorners)
    #     cv2.drawContours(imgDbg, debugPlayAreaContours, -1, (255, 0, 0), 3)

    # Draw contours
    cv2.drawContours(imgDbg, contours, -1, (0, 255, 0), 3)

    if len(closestToSquareCorners) != 4:
        print("Game area corners not found")
        return False, None, imgDbg

    # Debug

    # Warp the image back to right rectangle
    im_out = GameImageHandler.warpImageToRightRect(resizedImg, closestToSquareCorners, 300, -5)

    return True, im_out, imgDbg

def extractGameBoardUsingLines(img):

    # Open image and resize
    resizedImg = cv2.resize(img, (640, int(640*img.shape[0]/img.shape[1])), interpolation=cv2.INTER_CUBIC)
    imgDbg = resizedImg.copy()
    xRes = resizedImg.shape[1]
    yRes = resizedImg.shape[0]
    # print("xRes", xRes, "yRes", yRes)

    # Find lines in image
    candLines = GameImageHandler.findLinesInImage(resizedImg, imgDbg)
    if len(candLines) < 4:
        print("Not enough lines to find a rectangle")
        return False, None, imgDbg

    # Find the smallest large-enough rectangle close to the centre of the image
    rectSides = GameImageHandler.findRectangleAroundPoint(candLines, (xRes / 2, yRes / 2), xRes / 4)

    # Check we found a valid rect
    for side in rectSides:
        if not side:
            print("One or more sides of the rectangle can't be found")
            return False, None, imgDbg

    # Find corners of rectangle
    cornerPts = GameImageHandler.findRectangleCorners(rectSides)
    if len(cornerPts) != 4:
        print("Not enough corners found")
        return False, None, imgDbg

    # Rearrange the corners so the top left corner is first and corners are clockwise
    corners = GameImageHandler.normalizeCorners(cornerPts)

    # Warp the image back to right rectangle
    im_out = GameImageHandler.warpImageToRightRect(resizedImg, corners, 300, -5)

    return True, im_out, imgDbg

def extractTilesFromImage(img, crop):
    # Split image into 16 cells
    imOutXRes = img.shape[1]
    imOutYRes = img.shape[0]
    xCells = 4
    yCells = 4
    imgCells = []
    for yIdx in range(yCells):
        for xIdx in range(xCells):
            tlx = xIdx * imOutXRes / xCells
            tly = yIdx * imOutYRes / yCells
            wid = imOutXRes / xCells
            hig = imOutYRes / yCells
            cellImg = img[tly+crop:tly + hig - crop, tlx+crop:tlx + wid - crop]
            imgCells.append(cellImg)
    return imgCells

def getTileValue(img, tileImgsAndValues):

    # First check std-dev of image to see if tile is blank
    means, stdDevs = cv2.meanStdDev(img)
    maxStdDev = np.amax(stdDevs)
    stdDevThreshold = 7.5
    if maxStdDev < stdDevThreshold:
        print("Blank tile detected using std-dev " + str(maxStdDev))
        return " "

    bestMatchValue = "X"
    bestMatchFactor = 0
    imgInGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    for imgAndValue in tileImgsAndValues:
        # Apply template Matching
        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(imgInGray, imgAndValue["img"], method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if bestMatchFactor < max_val:
            bestMatchFactor = max_val
            bestMatchValue = imgAndValue["value"]

    threshold = 0.7
    if bestMatchFactor > threshold:
        print("Found match to value " + bestMatchValue + " matchFactor " + str(bestMatchFactor) + " maxColrStdDev " + str(maxStdDev))
        return bestMatchValue

    return "X"

def loadTileDefsFromJsonFile(jsonMapFileName, tileBasePath):

    # Load json file
    try:
        jsonFile = open(jsonMapFileName, "r")
    except IOError:
        print ("loadTileDefsFromJsonFile: Cannot open json tile definitions file " + jsonMapFileName)
        return None
    try:
        tileDefs = json.load(jsonFile)
    except:
        print("loadTileDefsFromJsonFile: Failed to decode JSON file " + jsonMapFileName)
        return None
    jsonFile.close()
    # Check file valid
    if not "fnameToValue" in tileDefs:
        print("loadTileDefsFromJsonFile: JSON file doesn't contain fnameToValue " + jsonMapFileName)
        exit(0)
    # Load the tiles into memory array
    tileImgsAndValues = []
    for fname in tileDefs["fnameToValue"]:
        tileImg = cv2.imread(tileBasePath + fname, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        if tileImg is None:
            print("loadTileDefsFromJsonFile: Can't open tile image " + fname)
        tileImgsAndValues.append({"img": tileImg, "value": tileDefs["fnameToValue"][fname]})
    return tileImgsAndValues
