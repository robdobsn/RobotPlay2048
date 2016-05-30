
import cv2
import numpy as np
import picamera
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

if __name__ == '__main__' :

    # Acquire source image.
    cam = picamera.PiCamera()
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

    cv2.imwrite('img23.png', im_out)

    # Match to template tiles
    tileFiles = ['tile000002.png', 'tile000004.png', 'tile000008.png',
                 'tile000016.png', 'tile000032.png', 'tile000064.png',
                 'tile000128.png', 'tile000256.png', 'tile000512.png',
                 'tile001024.png']
    lineThicknessIdx = 1
    tileVal = 2

    boardCells = [0] * 16
    for tileFile in tileFiles:
        tile = cv2.imread(tileFile, 0)
        w, h = tile.shape[::-1]

        # Apply template Matching
        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(im_grey, tile, method)
        threshold = 0.8
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            sq, sqValid = identifySq(pt, w, h)
            if sqValid:
                if boardCells[sq] == 0:
                    boardCells[sq] = tileVal
                    cv2.putText(im_out, str(tileVal), (pt[0],pt[1]+h/3),cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, 0, 1)
                #print(sq, tileVal)
#            print(pt, tileVal, w, h)
            #cv2.rectangle(im_out, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), lineThicknessIdx)
        lineThicknessIdx += 1
#        print("Found", len(zip(*loc[::-1])),"tiles of", tileVal)
        tileVal *= 2

    for cellIdx in range(len(boardCells)):
        print(cellIdx, boardCells[cellIdx])
    

    cv2.imshow("Matched One", im_out)

    cv2.waitKey(1000)
#    time.sleep(5)
    
