# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()

# allow the camera to warmup
time.sleep(0.1)

for xres in [320, 640, 1280]:

    # to speed things up, lower the resolution of the camera
    camera.resolution = (xres, xres*240/320)

    # grab images from the camera
    nowT = time.time()
    for i in range(10):
        rawCapture = PiRGBArray(camera)
        camera.capture(rawCapture, format="bgr")
        image = rawCapture.array
    print("At X resolution", xres, "Captured 10 images in ", time.time()-nowT, "secs")

    cv2.imwrite('testCameraRaw_out' + str(xres) + '.jpg',image)
