import picamera
import cv2
import io
import numpy as np
import time

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

    for xres in [320, 640, 1280]:

        print(xres)
        
        # set the resolution of the camera
        camera.resolution = (xres, xres*240/320)

        nowT = time.time()
        for i in range(10):
            image = captureImage(camera)
    
        print("At X resolution", xres, "Captured 10 images in ", time.time()-nowT, "secs")
    
        cv2.imwrite('testCameraFromVideo' + str(xres) + '.jpg',image)
