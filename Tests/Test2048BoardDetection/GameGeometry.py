import math
import numpy as np

#
# line segment intersection using vectors
# see Computer Graphics by F.S. Hill
#
def segPerp(a) :
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