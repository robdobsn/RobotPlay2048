
import cv2
import numpy as np

if __name__ == '__main__' :

    # Read source image.
    im_src = cv2.imread('img19small.png')
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

    # Display images
#    cv2.imshow("Source Image", im_src)
#    cv2.imshow("Destination Image", im_dst)
#    cv2.imshow("Warped Source Image", im_out)

    # Write out image
    # cv2.imwrite("imgout17.png", im_out)

    im_grey = cv2.cvtColor(im_out, cv2.COLOR_BGR2GRAY)

    tile000008 = cv2.imread('tile000008.png', 0)
#    tile000008 = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
    w, h = tile000008.shape[::-1]

    # Apply template Matching
    method = cv2.TM_CCOEFF_NORMED
    res = cv2.matchTemplate(im_grey, tile000008, method)

    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #
    # # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    # if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
    #     top_left = min_loc
    # else:
    #     top_left = max_loc
    # bottom_right = (top_left[0] + w, top_left[1] + h)
    # cv2.rectangle(im_grey, top_left, bottom_right, 255, 2)

    threshold = 0.8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(im_grey, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

    cv2.imshow("Matched One", im_grey)

    cv2.waitKey(0)
