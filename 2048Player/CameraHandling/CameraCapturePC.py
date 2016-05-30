import cv2

class CameraCapturePC:

    def __init__(self):
        # Camera port - need to set
        self.cameraPort = 0
        # Number of frames to throw away while the camera adjusts to light levels
        self.rampFrames = 1
        self.firstUse = True
        # Camera object
        self.camera = cv2.VideoCapture(self.cameraPort)

    def __del__(self):
        # Close the camera
        del(self.camera)

    def _rawGet(self):
        retval, img = self.camera.read()
        return img

    def captureImage(self):
        for i in xrange(self.rampFrames if not self.firstUse else 20):
            self._rawGet()
        self.firstUse = False
        return self._rawGet()

    def setResolution(self, x, y):
        # Does nothing here
        if self.camera.isOpened():
            self.camera.set(3,x)
            self.camera.set(4,y)
