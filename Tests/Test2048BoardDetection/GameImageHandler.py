import cv2
import numpy as np

import GameGeometry

# Find the lines in an image using Hough line transform
def findLinesInImage(img, imgDebug=None):
    xRes = img.shape[1]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 200, apertureSize=3)
    lines = cv2.HoughLines(edges,1,np.pi/180,int(xRes/6.0))
    if lines == None:
        print("No lines found")
        return []

    #	print(len(lines))
#	print(lines)
    candLines = []
    for line in lines:
        for rho,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*a)
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*a)
            candLines.append({"rho":rho, "theta":theta, "p1": np.array((x1, y1)), "p2":np.array((x2, y2)), "intersects":[]})
            if not imgDebug is None:
                cv2.line(imgDebug,(x1,y1),(x2,y2),(0,0,255),2)
    return candLines

def findRectangleAroundPoint(candLines, pt, minRectEdgeLen):
    # Sort the potential lines by distance from point
    nearLines = sorted(candLines, key=lambda lin: GameGeometry.distSqPtToLine(lin["p1"], lin["p2"], pt))
    # for lin in nearLines:
    # 	print(lin)

    # Assume the nearest line is part of the rect we want
    rectSideIdxs = [0, -1, -1, -1]
    line1To3BestSep = 1000000
    line0To2BestSep = 1000000
    # Find lines which form a rectangle with edges long enough to meet our criteria
    for linIdx in range(1, len(nearLines)):
        # print(isOrthogonal(line1, candLines[linIdx]), linIdx)
        if GameGeometry.isOrthogonal(nearLines[rectSideIdxs[0]], nearLines[linIdx]):
            if rectSideIdxs[1] == -1:
                rectSideIdxs[1] = linIdx
            else:
                lineSep = GameGeometry.lineSeparation(nearLines[rectSideIdxs[1]], nearLines[linIdx])
#				print("LineSep", lineSep, rectSideIdxs[1], linIdx)
                if lineSep > minRectEdgeLen:
                    if line1To3BestSep > lineSep:
                        rectSideIdxs[3] = linIdx
                        line1To3BestSep = lineSep
        else:
            lineSep = GameGeometry.lineSeparation(nearLines[rectSideIdxs[0]], nearLines[linIdx])
            if lineSep > minRectEdgeLen:
                if line0To2BestSep > lineSep:
                    rectSideIdxs[2] = linIdx
                    line0To2BestSep = lineSep

#	print("Rect Side Idxs", rectSideIdxs)
    sides = []
    for i in rectSideIdxs:
        if i != -1:
            sides.append(nearLines[i])
        else:
            sides.append(None)
    return sides

def findRectangleCorners(sides, imgDbg=None):
    # Find the intersection points of the sides of the rectangle
    intPts = []
    for rectSideIdx in range(len(sides)):
        # print("Checking intersect of", sides[rectSideIdx], sides[(rectSideIdx+1)%4])
        l1 = sides[rectSideIdx]
        l2 = sides[(rectSideIdx + 1) % 4]
        intValid, pt = GameGeometry.seg_intersect(l1["p1"], l1["p2"], l2["p1"], l2["p2"])
        if intValid:
            intPts.append(pt)
            if imgDbg:
                colr = [(0, 0, 0), (250, 0, 0), (0, 250, 0), (0, 0, 250)]
                cv2.circle(imgDbg, (int(pt[0]), int(pt[1])), 5, colr[rectSideIdx], 0)
#			print(pt, rectSideIdx * 50)
        else:
#			print("No intersection of rectangle sides")
            return []
    return intPts

# This from here http://stackoverflow.com/questions/4437986/how-to-find-direction-of-a-vector-path
def isClockwise(pt0, pt1, pt2):
    return (pt1[0] - pt0[0]) * (pt2[1] - pt1[1]) - (pt1[1] - pt0[1]) * (pt2[0] - pt1[0]) > 0

def normalizeCorners(corners):
    # Work out if rectangle is clockwise or anti-clockwise
    rectIsClockwise = isClockwise(corners[0], corners[1], corners[2])
#	print("Clockwise", rectIsClockwise)

    # Find the top left corner of the rectangle and rearrange vertices to make clockwise
    tlPointSum = 1000000
    tlIdx = 0
    for ptIdx in range(len(corners)):
        if tlPointSum > corners[ptIdx][0] + corners[ptIdx][1]:
            tlPointSum = corners[ptIdx][0] + corners[ptIdx][1]
            tlIdx = ptIdx
    tmpPts = corners[:]
    srcIdx = tlIdx
    for ptIdx in range(len(corners)):
        corners[ptIdx] = tmpPts[srcIdx]
#		print(corners[ptIdx])
        if rectIsClockwise:
            srcIdx += 1
            if srcIdx >= len(corners):
                srcIdx = 0
        else:
            srcIdx -= 1
            if srcIdx < 0:
                srcIdx = len(corners) - 1
    return corners

def warpImageToRightRect(inImg, corners, destXRes, borderPix):
    pts_src = np.array(corners, dtype=float)
    # Form blank destination image
    xPixels = destXRes
    yPixels = (xPixels * inImg.shape[0] / inImg.shape[1])
    brd = borderPix
    im_dst = np.zeros((xPixels, yPixels, 3), np.uint8)
    # Four corners to map to
    pts_dst = np.array([[yPixels - 1 - brd, brd], [yPixels - 1 - brd, xPixels - 1 - brd], \
                    [brd, xPixels - 1 - brd], [brd, brd]], dtype=float)

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    return cv2.warpPerspective(inImg, h, (im_dst.shape[1], im_dst.shape[0]))

