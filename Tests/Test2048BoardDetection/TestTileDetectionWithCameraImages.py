
import cv2
import time
import Game2048ImageProc
#import CameraCaptureRaspPi
from CameraCapturePC import CameraCapturePC

extractTiles = False

tileImgsAndValues = Game2048ImageProc.loadTileDefsFromJsonFile("../TestOutputs/Tiles/tileDefs.json", "../TestOutputs/Tiles/")
if tileImgsAndValues is None:
    print("Can't open Json file")
    exit(0)

#cameraCapture = CameraCaptureRaspPi()
cameraCapture = CameraCapturePC()
cameraCapture.setResolution(1280, 1024)

# Loop capturing images and interpreting
while(True):
    # Get image
    image = cameraCapture.captureImage()

    # Show captured image
    cv2.imshow("captured", image)

    # Get the board
    rslt, imOut, imgDebug = Game2048ImageProc.extractGameBoard(image)
    if not rslt:
        print("Unable to extract game board")
        # Show debug image
        cv2.imshow("debug", imgDebug)
        cv2.destroyWindow("output")
        # Wait and check for escape key
        keyPress = cv2.waitKey(0)
        if keyPress == 27:
            exit(0)
        continue

    # Show debug image
    cv2.imshow("debug", imgDebug)
    cv2.imshow("output", imOut)

    # Copy image for annotation
    if extractTiles:
        imgAnnotated = imOut.copy()

        boardVals = []
        if rslt:
            imgTiles = Game2048ImageProc.extractTilesFromImage(imOut, 5)
            for imgIdx in range(len(imgTiles)):
                tileVal = Game2048ImageProc.getTileValue(imgTiles[imgIdx], tileImgsAndValues)
                boardVals.append(tileVal)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(imgAnnotated, tileVal, (60 * (imgIdx % 4) + 5, 75 * (imgIdx / 4) + 30), font, 0.5, (255, 255, 255), 2)
                 # print("Tile value found = ", tileVal)
                # cv2.imshow("tile", imgTiles[imgIdx])
                # keyPress = cv2.waitKey(0)
                # if keyPress == 27:
                #     exit(0)

        # Show result
        cv2.imshow("result", imgAnnotated)

    # Wait and check for escape key
    keyPress = cv2.waitKey(0)
    if keyPress == 27:
        exit(0)

