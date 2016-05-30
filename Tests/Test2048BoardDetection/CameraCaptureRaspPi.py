import picamera
import numpy as np
import cv2
import time
import io

class CameraCaptureRaspPi:

    def __init__(self):
        self.camera = picamera.PiCamera()
        # allow the camera to warm up
        time.sleep(0.1)

    def captureImage(self):
        # saving the picture to an in-program stream rather than a file
        stream = io.BytesIO()
        # capture into stream
        self.camera.capture(stream, format='jpeg', use_video_port=True)
        # convert image into numpy array
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        # turn the array into a cv2 image
        img = cv2.imdecode(data, 1)
        return img

    def setResolution(self, x, y):
        # set the resolution of the camera
        self.camera.resolution = (x,y)
