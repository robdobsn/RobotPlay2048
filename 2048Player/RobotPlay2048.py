import cv2
import time
from BoardRecogniser import Game2048ImageProc
from RobotControl import Game2048RobotControl
from GameLogic import Game2048GameLogic
import serial

RUN_TARGET = "PC"
if RUN_TARGET == "PC":
    from CameraHandling import CameraCapturePC
    cameraCapture = CameraCapturePC.CameraCapturePC()
    serialPortName = ""
elif RUN_TARGET == "RaspPi":
    from CameraHandling import CameraCaptureRaspPi
    cameraCapture = CameraCaptureRaspPi()
    serialPortName = "/dev/ttyAMA0"
else:
    print("Don't know that run target")
    exit(0)

# Tile definitions
tileImgsAndValues = Game2048ImageProc.loadTileDefsFromJsonFile("../Tests/TestOutputs/Tiles/tileDefs.json", "../Tests/TestOutputs/Tiles/")
if tileImgsAndValues is None:
    print("Can't open Json file")
    exit(0)

# Camera resolution
cameraCapture.setResolution(1280, 1024)

# Serial port for robot comms
serialPort = None
if serialPortName is not "":
    try:
        serialPort = serial.Serial(serialPortName, baudrate=115200, timeout=3.0)
    except:
        print("Serial port " + serialPortName + " cannot be opened")
        exit(0)
else:
    print("Running without robot control as serial port name empty")

# Robot control
robotControl = Game2048RobotControl.RobotControl()
robotControl.setSerialPort(serialPort)
robotControl.goCentre()

# Game logic
gameLogic = Game2048GameLogic.Game2048Logic()

# Loop capturing images and interpreting
cameraFailCount = 0
while(True):

    # Get image
    image = cameraCapture.captureImage()

    # Show captured image
    cv2.imshow("captured", image)

    # Get the board
    rslt, imOut, imgDebug = Game2048ImageProc.extractGameBoard(image)
    if not rslt:
        cameraFailCount += 1
        if cameraFailCount > 10:
            print("Failed to extract game board from camera image")
            exit(0)
        time.sleep(0.25)
        continue

    # Show debug image
    cv2.imshow("debug", imgDebug)

    # Copy image for annotation
    imgAnnotated = imOut.copy()

    boardCells = []
    if rslt:
        imgTiles = Game2048ImageProc.extractTilesFromImage(imOut, 5)
        for imgIdx in range(len(imgTiles)):
            tileVal = Game2048ImageProc.getTileValue(imgTiles[imgIdx], tileImgsAndValues)
            boardCells.append(tileVal)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(imgAnnotated, tileVal, (60 * (imgIdx % 4) + 5, 75 * (imgIdx / 4) + 30), font, 0.5, (255, 255, 255), 2)
            # print("Tile value found = ", tileVal)
            # cv2.imshow("tile", imgTiles[imgIdx])
            # keyPress = cv2.waitKey(0)
            # if keyPress == 27:
            #     exit(0)

    # Show result
    cv2.imshow("result", imgAnnotated)

    # Get the best move
    bestMove = gameLogic.pickAMove(boardCells)

    # Wait and check for escape key
    keyPress = cv2.waitKey(0)
    if keyPress == 27:
        exit(0)

