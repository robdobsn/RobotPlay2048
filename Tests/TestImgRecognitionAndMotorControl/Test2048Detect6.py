
import cv2
import numpy as np
import picamera
import serial
import time

def identifySq(pt, w, h):
    tlx = 80
    tly = 210
    ppx = 94
    ppy = 82
    sqx = (pt[0]-(tlx-ppx/2))/ppx
    sqy = (pt[1]-(tly-ppy/2))/ppy
    # print ("ID",pt, w, h, sqx, sqy)
    if sqx < 0 or sqx >= 4 or sqy < 0 or sqy >= 4:
        return 0, False
    return sqy*4 + sqx, True

def extractBoard(cam):

    # Acquire source image.
    cam.capture('newimg.jpg')

    # Read source image.
    im_src = cv2.imread('newimg.jpg')
 
    # Resize image
    newWidth = 640.0
    rat1 = newWidth / im_src.shape[1]
    dim1 = (int(newWidth), int(im_src.shape[0] * rat1))
    im_small = cv2.resize(im_src, dim1, interpolation = cv2.INTER_AREA)
    
    # Four corners of the book in source image
    pts_src = np.array([[57, 368], [98, 22], [585, 28], [626, 374]], dtype=float)

    # Read destination image.
    im_dst = cv2.imread('destimg2.jpg')
    # Four corners of the book in destination image.
    pts_dst = np.array([[0, 0], [511, 0], [511, 639], [0, 639]], dtype=float)

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(im_small, h, (im_dst.shape[1], im_dst.shape[0]))
    im_grey = cv2.cvtColor(im_out, cv2.COLOR_BGR2GRAY)

    cv2.imwrite('img30.png', im_out)

    # Match to template tiles
    tileFiles = ['tile000002.png', 'tile000004.png', 'tile000008.png',
                 'tile000016.png', 'tile000032.png', 'tile000064.png',
                 'tile000128.png', 'tile000256.png', 'tile000512.png',
                 'tile001024.png']
    lineThicknessIdx = 1
    tileVal = 2

    boardCells = [0] * 16
    candidatesFound = []
    for tileFile in tileFiles:
        tile = cv2.imread(tileFile, 0)
        w, h = tile.shape[::-1]

        # Apply template Matching
        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(im_grey, tile, method)
        threshold = 0.9
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            sq, sqValid = identifySq(pt, w, h)
            if sqValid:
                candidatesFound.append([sq, tileVal, res])
        tileVal *= 2

    candidatesFound.sort(key=lambda cand: cand[0])
    posVals = []
    curSq = 0
    for cand in candidatesFound:
        sq = cand[0]
        tileVal = cand[1]
        if sq != curSq:
            posVals.sort(key=lambda pos: pos[1])
            if len(posVals) > 0 and posVals[len(posVals)-1] != 0:
                boardCells[curSq] = posVals[len(posVals)-1][0]
            posVals = []
            curSq = sq
        else:
            foundVal = False
            for posVal in posVals:
                if tileVal == posVal[0]:
                    posVal[1] += 1
                    foundVal = True
            if not foundVal:
                posVals.append([tileVal, 1])
    posVals.sort(key=lambda pos: pos[1])
    if len(posVals) > 0 and posVals[len(posVals)-1] != 0:
        boardCells[curSq] = posVals[len(posVals)-1][0]
                
#        if boardCells[sq] == 0:
#            boardCells[sq] = tileVal

#    for cell in boardCells:
#        cv2.putText(im_out, str(tileVal), (pt[0],pt[1]+h/3),cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, 0, 1)
                #print(sq, tileVal)
#            print(pt, tileVal, w, h)
            #cv2.rectangle(im_out, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), lineThicknessIdx)
#        lineThicknessIdx += 1
#        print("Found", len(zip(*loc[::-1])),"tiles of", tileVal)

#    cv2.imshow("Matched One", im_out)
#    cv2.waitKey(1000)

    return boardCells

centrePos = b'G0 0 130'
straightPos = b'G0 0 200'

def writeSerialCmd(cmd, delay=0.2):
    serialPort.write(cmd)
    serialPort.write(b'\r\n')
    time.sleep(delay)
    
def makeMove(serialPort, dirn, afterDelay=0.0):
    downPen = b'P1'
    upPen = b'P0'
    leftPos = b'G0 0 110'
    upPos = b'G0 -20 130'
    rightPos = b'G0 0 150'
    downPos = b'G0 15 130'
    moves = []
    if dirn == 'left':
        moves = [downPen, leftPos, upPen, centrePos]
    elif dirn == 'up':
        moves = [downPen, upPos, upPen, centrePos]
    elif dirn == 'right':
        moves = [downPen, rightPos, upPen, centrePos]
    elif dirn == 'down':
        moves = [downPen, downPos, upPen, centrePos]
    for move in moves:
        writeSerialCmd(move)
    time.sleep(afterDelay)

def algo1(boardCells):
    dirns = ['left','up','down','right']
    bestDir = ""
    bestCombines = 0
    bestCombineSum = 0
    bestMoveCount = 0
    bestBoard = []
    for dir in dirns:
        cellMap = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        if dir == 'left':
            cellMap = [12,8,4,0,13,9,5,1,14,10,6,2,15,11,7,3]
        elif dir == 'down':
            cellMap = [15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
        elif dir == 'right':
            cellMap = [3,7,11,15,2,6,10,14,1,5,9,13,0,4,8,12]
        newBoard = boardCells[:]
        combines = 0
        combineSum = 0
        moveCount = 0
        movesMade = True
        while(movesMade):
            movesMade = False
            for cellIdx in range(12):
                if newBoard[cellMap[cellIdx]] == 0:
                    for idx in range(3 - cellIdx/4):
                        if newBoard[cellMap[cellIdx+4+idx*4]] != 0:
                            newBoard[cellMap[cellIdx+idx*4]] = newBoard[cellMap[cellIdx+4+idx*4]]
                            newBoard[cellMap[cellIdx+4+idx*4]] = 0
                            movesMade = True
                            moveCount += 1
        for cellIdx in range(12):
            if newBoard[cellMap[cellIdx]] != 0 and newBoard[cellMap[cellIdx]] == newBoard[cellMap[cellIdx+4]]:
                combines += 1
                combineSum += boardCells[cellMap[cellIdx]] * 2
                newBoard[cellMap[cellIdx]] *= 2
                newBoard[cellMap[cellIdx+4]] = 0
                for idx in range(2 - cellIdx/4):
                    newBoard[cellMap[cellIdx+4+idx*4]] = newBoard[cellMap[cellIdx+8+idx*4]]
                    newBoard[cellMap[cellIdx+8+idx*4]] = 0
        print(dir,"num combines", combines, "Sum", combineSum,"MoveCount", moveCount)
        if (bestCombines + bestMoveCount == 0 and combines + moveCount > 0) or \
            (bestCombineSum < combineSum) or \
            (bestMoveCount < moveCount and combineSum == bestCombineSum):
            bestCombines = combines
            bestDir = dir
            bestCombineSum = combineSum
            bestMoveCount = moveCount
            bestBoard = newBoard[:]
            
    print("Best Dir", bestDir)
    return bestBoard, bestDir

def compareToPrev(curBoard, prevBoard):
    if len(prevBoard) != 16:
        return
    numDiffs = 0
    for ii in range(len(curBoard)):
        if curBoard[ii] != prevBoard[ii]:
            if numDiffs == 0:
                if curBoard[ii] == 2 or curBoard[ii] == 4:
                    print("New tile is", curBoard[ii],"at pos", ii)
                else:
                    print("ERROR IN BOARD POS AT", ii, "VAL NOT 2 OR 4")
            else:
                print("ERROR IN BOARD POS AT", ii, "MORE THAN ONE DIFF")
            numDiffs += 1

if __name__ == '__main__' :
    cam = picamera.PiCamera()
    with serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=3.0) as serialPort:
        writeSerialCmd(centrePos, 2.0)

        prevBoard = []
        for moveIdx in range(1000):
            boardCells = extractBoard(cam)
            if sum(boardCells) == 0:
                print("Can't see board")
                break
            print("Current", boardCells)
            compareToPrev(boardCells, prevBoard)
            newBoard, bestDir = algo1(boardCells)
            if bestDir == "":
                print("No moves can be made")
                break
            makeMove(serialPort, bestDir, 1.0)
            print("Expected", newBoard)
            prevBoard = newBoard[:]

        writeSerialCmd(straightPos, 2.0)
        
