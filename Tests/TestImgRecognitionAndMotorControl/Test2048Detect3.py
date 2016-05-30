
import cv2
import numpy as np

if __name__ == '__main__' :

    # Read source image.
    im_src = cv2.imread('img17small.png')
    # Four corners of the book in source image
    pts_src = np.array([[57, 368], [98, 22], [585, 28], [626, 374]], dtype=float)

    # Read destination image.
    im_dst = cv2.imread('destimg2.jpg')
    # Four corners of the book in destination image.
    pts_dst = np.array([[0, 0], [511, 0], [511, 639], [0, 639]], dtype=float)

    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(im_src, h, (im_dst.shape[1], im_dst.shape[0]))
    im_grey = cv2.cvtColor(im_out, cv2.COLOR_BGR2GRAY)

    # Match to template tiles
    tileFiles = ['tile000002.png', 'tile000004.png', 'tile000008.png',
                 'tile000016.png', 'tile000032.png', 'tile000064.png',
                 'tile000128.png']
    lineThicknessIdx = 1

    for tileFile in tileFiles:
        tile = cv2.imread(tileFile, 0)
        w, h = tile.shape[::-1]

        # Apply template Matching
        method = cv2.TM_CCOEFF_NORMED
        res = cv2.matchTemplate(im_grey, tile, method)
        threshold = 0.75
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(im_grey, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), lineThicknessIdx)
        lineThicknessIdx += 1

    cv2.imshow("Matched One", im_grey)

    cv2.waitKey(0)
