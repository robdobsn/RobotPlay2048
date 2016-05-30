import time

class RobotControl:

    def __init__(self):
        self.commands = {
            "centre":  b'G0 0 130',
            "straight": b'G0 0 200',
            "penDown": b'P1',
            "penUp": b'P0',
            "left": b'G0 0 110',
            "up": b'G0 -20 130',
            "right": b'G0 0 150',
            "down": b'G0 15 130',
        }
        self.serialPort = None

    def setSerialPort(self, port):
        self.serialPort = port

    def sendSerialCmd(self, cmd, delay=0.2):
        if self.serialPort is None:
            return
        self.serialPort.write(self.commands[cmd])
        self.serialPort.write(b'\r\n')
        time.sleep(delay)

    def makeMove(self, dirn, afterDelay=0.0):
        moves = ["penDown"]
        moves.append(dirn)
        moves.append(["penUp", "centre"])
        for move in moves:
            self.sendSerialCmd(move)
        time.sleep(afterDelay)

    def goCentre(self):
        self.sendSerialCmd("centre")

    def goStraight(self):
        self.sendSerialCmd("straight")
