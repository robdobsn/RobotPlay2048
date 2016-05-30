import picamera
import cv2
import io
import numpy as np
import time
import os.path

def captureImage(camera):
    # saving the picture to an in-program stream rather than a file
    stream = io.BytesIO()

    # capture into stream
    camera.capture(stream, format='jpeg', use_video_port=True)
    # convert image into numpy array
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    # turn the array into a cv2 image
    img = cv2.imdecode(data, 1)

    return img

with picamera.PiCamera() as camera:

    # allow the camera to warmup
    time.sleep(0.1)

    # Get file name base
    fnameBase = ""
    for i in range(10000):
        fnameBaseTest = "../TestImgs/Mobwis/Test2048Img_"+str(i)+"_"
        fnameTest = fnameBaseTest+"320.jpg"
        if not os.path.isfile(fnameTest):
            fnameBase = fnameBaseTest
            break
    if fnameBase == "":
        print("Can't find a suitable name")
        exit(0)

    for xres in [320, 640, 1280]:

        # set the resolution of the camera
        camera.resolution = (xres, xres*240/320)

        nowT = time.time()
        image = captureImage(camera)
        fname = fnameBase + str(xres) + '.jpg'
        print("Captured to",fname,"X res", xres, "in ", time.time()-nowT, "secs")

        cv2.imwrite(fname,image)
