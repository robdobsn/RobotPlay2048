import picamera
import cv2
import io
import numpy as np
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

def detect_red(camera):
    # saving the picture to an in-program stream rather than a file
    stream = io.BytesIO()

    #scale_down = 6
    red = False

    # capture into stream
    camera.capture(stream, format='jpeg', use_video_port=True)
    # convert image into numpy array
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    # turn the array into a cv2 image
    img = cv2.imdecode(data, 1)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    cv2.imwrite('houghlines3gray.jpg',gray)
    edges = cv2.Canny(gray,100,200,apertureSize = 3)
    cv2.imwrite('houghlines3edges.jpg',edges)

    lines = cv2.HoughLines(edges,1,np.pi/180,200)
    print(edges)
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

    cv2.imwrite('houghlines3.jpg',img)


    # Resizing the image, blur the image and convert it to HSV values for better recognition
    # img = cv2.resize(img, (len(img[0]) / scale_down, len(img) / scale_down))
    # img = cv2.GaussianBlur(img, (5,5), 0)
#    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #Defining the red color range and calculating if these values lie in the range
#    red_lower = np.array([0, 150, 0], np.uint8)
#    red_upper = np.array([5, 255, 255], np.uint8)
#    red_binary = cv2.inRange(img, red_lower, red_upper)

    # Dilates the red space, making it larger
#    dilation = np.ones((15, 15), "uint8")
#    red_binary = cv2.dilate(red_binary, dilation)

#    contours, _ = cv2.findContours(red_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

#    if not contours == []:
#        if not red:
#            red = True
#            print "Red surface detected!"
#    else:
#        print "No red surface  detected."

#    return red

    nowT = time.time()
    
    # Four corners of the book in source image
    pts_src = np.array([[57, 368], [98, 22], [585, 28], [626, 374]], dtype=float)

    # Four corners of the book in destination image.
    pts_dst = np.array([[0, 0], [511, 0], [511, 639], [0, 639]], dtype=float)

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(img, h, (640, 512))
    im_grey = cv2.cvtColor(im_out, cv2.COLOR_BGR2GRAY)

    # cv2.imwrite('img24.png', im_out)

    print((time.time()-nowT)*1000)

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
        nowT = time.time()
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
        print((time.time()-nowT)*1000)

    nowT = time.time()
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

    print((time.time()-nowT)*1000)
                
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



with picamera.PiCamera() as camera:
    # to speed things up, lower the resolution of the camera
    camera.resolution = (320, 240)
    cells = detect_red(camera)
    print(cells)
    detect_red(camera)
    detect_red(camera)
    detect_red(camera)
    # and so on...
