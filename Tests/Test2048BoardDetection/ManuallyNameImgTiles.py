import cv2
import os
import json

jsonMapFileName = "../TestOutputs/Tiles/tileDefs.json"
tileDefs = { "fnameToValue": {} }
with open(jsonMapFileName, "r") as jsonFile:
    tileDefs = json.load(jsonFile)

for subdir, dirs, files in os.walk("../TestOutputs/Tiles"):
    for fil in files:
        fname = subdir + os.sep + fil
        if not fname.endswith(".jpg"):
            continue

        img = cv2.imread(fname)
        xRes = img.shape[1]
        yRes = img.shape[0]

        # Check if we have this tile
        tileValue = "UN"
        if fil in tileDefs["fnameToValue"]:
            tileValue = tileDefs["fnameToValue"][fil]

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, tileValue, (0, 20), font, 1, (255, 255, 255), 2)

        cv2.imshow("tile", img)
        keyPress = cv2.waitKey(0)
        #print (keyPress)

        if keyPress == ord("X") or keyPress == ord("x") or keyPress == 27:
            break

        if keyPress == ord(" "):
            continue

        if keyPress >= ord("1") and keyPress <= ord("9"):
            tileValue = str(2**(keyPress-ord("0")))
        elif keyPress >= ord("A") and keyPress <= ord("H"):
            tileValue = str(2**(keyPress-ord("A")+10))

        if tileValue is not "UN":
            print("New tile value " + str(tileValue))
            tileDefs["fnameToValue"][fil] = tileValue

with open(jsonMapFileName, "w") as jsonFile:
    json.dump(tileDefs, jsonFile)
