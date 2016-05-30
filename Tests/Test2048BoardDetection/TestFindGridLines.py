import cv2
import numpy as np
import math

#
# line segment intersection using vectors
# see Computer Graphics by F.S. Hill
#

def segPerp( a ) :
	b = np.empty_like(a)
	b[0] = -a[1]
	b[1] = a[0]
	return b

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# return
def seg_intersect(a1,a2, b1,b2):
	da = a2-a1
	db = b2-b1
	dp = a1-b1
	dap = segPerp(da)
	denom = np.dot( dap, db)
	num = np.dot( dap, dp )
	if denom == 0:
		return (False, (0,0))
	return (True, (num / denom.astype(float))*db + b1)

# Find if two lines are more or less orthogonal - can't be too precise as the
# image may be warped by perspective etc
def isOrthogonal(l1, l2):
	ang = (l1["theta"] - l2["theta"] + np.pi * 2) % np.pi
	return abs(ang - np.pi/2) < np.pi/4

# Calculate square of distance from a point to a line (for sorting)
def distSqPtToLineXY(x1, y1, x2, y2, xPt, yPt):
	dx = x2-x1
	dy = y2-y1
	sqdiff = dx*dx + dy*dy
	u = ((xPt - x1) * dx + (yPt - y1) * dy) / float(sqdiff)
	u = 0 if u < 0 else (1 if u > 1 else u)
	x = x1 + u * dx
	y = y1 + u * dy
	ddx = x - xPt
	ddy = y - yPt
	distSq = ddx*ddx + ddy*ddy
	return distSq

def distSqPtToLine(linePt1, linePt2, pt):
	return distSqPtToLineXY(linePt1[0], linePt1[1], linePt2[0], linePt2[1], pt[0], pt[1])

# Find the mid point of a line
def lineMidPt(line):
	return (((line["p1"][0]+line["p2"][0])/2, (line["p1"][1]+line["p2"][1])/2))

# Distance from pt to pt
def distPtToPt(p1, p2):
	dx = p1[0]-p2[0]
	dy = p1[1]-p2[1]
	return math.sqrt(dx*dx+dy*dy)

# Find separation distance of the mid-points of two lines
def lineSeparation(l1, l2):
	mid1 = lineMidPt(l1)
	mid2 = lineMidPt(l2)
#	print("Mids", l1, l2, mid1, mid2)
	return distPtToPt(mid1, mid2)

# Find the lines in an image using Hough line transform
def findLinesInImageNonProb(img, imgDebug=None):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	edges = cv2.Canny(gray, 50, 200, apertureSize=3)
	cv2.imshow("edges", edges)

	lines = cv2.HoughLines(edges,1,np.pi/180,int(xRes/6.0))
	if lines == None:
		print("No lines found")
		return []
	print(len(lines))
	print(lines)
	candLines = []
	for line in lines:
		for rho,theta in line:
			a = np.cos(theta)
			b = np.sin(theta)
			x0 = a*rho
			y0 = b*rho
			x1 = int(x0 + 1000*(-b))
			y1 = int(y0 + 1000*(a))
			x2 = int(x0 - 1000*(-b))
			y2 = int(y0 - 1000*(a))
			candLines.append({"rho":rho, "theta":theta, "p1": np.array((x1, y1)), "p2":np.array((x2, y2)), "intersects":[]})
			if imgDebug is not None:
				cv2.line(imgDebug,(x1,y1),(x2,y2),(0,0,255),2)
	if imgDebug is not None:
		cv2.imshow("lines", imgDebug)
		cv2.waitKey(0)
	return candLines

# Find the lines in an image using Hough line transform
def findLinesInImageProb(img, imgDebug=None):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	edges = cv2.Canny(gray, 50, 150, apertureSize=3)
	cv2.imshow("edges", edges)
	cv2.waitKey(0)
	lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, 1, 10)
	if lines == None:
		print("No lines found")
		return []

	print(len(lines))
	print(lines)
	candLines = []
	for x1, y1, x2, y2 in lines[0]:
		candLines.append(
			{"rho": 0, "theta": 0, "p1": np.array((x1, y1)), "p2": np.array((x2, y2)), "intersects": []})
		if imgDebug is not None:
			cv2.line(imgDebug, (x1, y1), (x2, y2), (0, 255, 0), 2)
	if imgDebug is not None:
		cv2.imshow("lines", imgDebug)
	cv2.waitKey(0)

	# for line in lines:
	# 	for rho,theta in line:
	# 		a = np.cos(theta)
	# 		b = np.sin(theta)
	# 		x0 = a*rho
	# 		y0 = b*rho
	# 		x1 = int(x0 + 1000*(-b))
	# 		y1 = int(y0 + 1000*(a))
	# 		x2 = int(x0 - 1000*(-b))
	# 		y2 = int(y0 - 1000*(a))
	# 		candLines.append({"rho":rho, "theta":theta, "p1": np.array((x1, y1)), "p2":np.array((x2, y2)), "intersects":[]})
	# 		if imgDebug is not None:
	# 			cv2.line(imgDebug,(x1,y1),(x2,y2),(0,0,255),2)
	return candLines

def findRectangleAroundPoint(candLines, pt, minRectEdgeLen):
	# Sort the potential lines by distance from point
	nearLines = sorted(candLines, key=lambda lin: distSqPtToLine(lin["p1"], lin["p2"], pt))
	for lin in nearLines:
		print(lin)

	# Assume the nearest line is part of the rect we want
	rectSideIdxs = [0, -1, -1, -1]
	line1To3BestSep = 1000000
	line0To2BestSep = 1000000
	# Find lines which form a rectangle with edges long enough to meet our criteria
	for linIdx in range(1, len(nearLines)):
		# print(isOrthogonal(line1, candLines[linIdx]), linIdx)
		if isOrthogonal(nearLines[rectSideIdxs[0]], nearLines[linIdx]):
			if rectSideIdxs[1] == -1:
				rectSideIdxs[1] = linIdx
			else:
				lineSep = lineSeparation(nearLines[rectSideIdxs[1]], nearLines[linIdx])
				print("LineSep", lineSep, rectSideIdxs[1], linIdx)
				if lineSep > minRectEdgeLen:
					if line1To3BestSep > lineSep:
						rectSideIdxs[3] = linIdx
						line1To3BestSep = lineSep
		else:
			lineSep = lineSeparation(nearLines[rectSideIdxs[0]], nearLines[linIdx])
			if lineSep > minRectEdgeLen:
				if line0To2BestSep > lineSep:
					rectSideIdxs[2] = linIdx
					line0To2BestSep = lineSep

	print("Rect Side Idxs", rectSideIdxs)
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
		intValid, pt = seg_intersect(l1["p1"], l1["p2"], l2["p1"], l2["p2"])
		if intValid:
			intPts.append(pt)
			if imgDbg:
				colr = [(0, 0, 0), (250, 0, 0), (0, 250, 0), (0, 0, 250)]
				cv2.circle(imgDbg, (int(pt[0]), int(pt[1])), 5, colr[rectSideIdx], 0)
			print(pt, rectSideIdx * 50)
		else:
			print("No intersection of rectangle sides")
			return []
	return intPts

# This from here http://stackoverflow.com/questions/4437986/how-to-find-direction-of-a-vector-path
def isClockwise(pt0, pt1, pt2):
	return (pt1[0] - pt0[0]) * (pt2[1] - pt1[1]) - (pt1[1] - pt0[1]) * (pt2[0] - pt1[0]) > 0

def normalizeCorners(corners):
	# Work out if rectangle is clockwise or anti-clockwise
	rectIsClockwise = isClockwise(corners[0], corners[1], corners[2])
	print("Clockwise", rectIsClockwise)

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
		print(corners[ptIdx])
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



########################################################
########################################################

# Start Program here

# Open image and resize
img = cv2.imread('../TestImgs/Free/Test2048Img_8_1280.jpg')
resizedImg = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
imgDbg = resizedImg.copy()
xRes = resizedImg.shape[1]
yRes = resizedImg.shape[0]
print("xRes", xRes, "yRes", yRes)

# Find lines in image
candLines = findLinesInImageNonProb(resizedImg, imgDbg)
if len(candLines) < 4:
	print("Not enough lines to find a rectangle")
	exit (0)

# Find the smallest large-enough rectangle close to the centre of the image
rectSides = findRectangleAroundPoint(candLines, (xRes/2, yRes/2), xRes/4)

# Check we found a valid rect
for side in rectSides:
	if not side:
		print("One or more sides of the rectangle can't be found")
		exit(0)

# Find corners of rectangle
cornerPts = findRectangleCorners(rectSides)
if len(cornerPts) != 4:
	print("Not enough corners found")
	exit(0)

# Rearrange the corners so the top left corner is first and corners are clockwise
corners = normalizeCorners(cornerPts)

# Warp the image back to right rectangle
im_out = warpImageToRightRect(resizedImg, corners, 300, 5)

# Split image into 16 cells
imOutXRes = im_out.shape[1]
imOutYRes = im_out.shape[0]
xCells = 4
yCells = 4
imgCells = []
for yIdx in range(yCells):
	for xIdx in range(xCells):
		tlx = xIdx*imOutXRes/xCells
		tly = yIdx*imOutYRes/yCells
		wid = imOutXRes/xCells
		hig = imOutYRes/yCells
		cellImg = im_out[tly:tly+hig, tlx:tlx+wid]
		imgCells.append(cellImg)

cv2.imshow("Output", imgDbg)
cv2.waitKey(0)
