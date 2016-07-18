from __future__ import print_function

class Game2048Logic:

    # The board is simply a list of integers representing the cells
    # First element is top-left and so on left-to-right and then
    # top-to-bottom as a raster

    # Board cells contain a string which represents the tile
    # number or " " if the tile is empty or "X" if it could not
    # be determined (assumed empty)

    def getCellVal(self, cellStr):
        try:
            return int(cellStr)
        except ValueError:
            return 0

    def pickAMove(self, boardCells):
        origBoard = []
        for cell in boardCells:
            origBoard.append(self.getCellVal(cell))
        print(origBoard)

        dirns = ['left','up','down','right']
        bestDir = ""
        bestCombines = 0
        bestCombineSum = 0
        bestMoveCount = 0
        bestBoard = []
        for dir in dirns:
            cellMap = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
            if dir == 'left':
                cellMap = [12,8,4,0,13,9,5,1,14,10,6,2,15,11,7,3]
            elif dir == 'down':
                cellMap = [15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
            elif dir == 'right':
                cellMap = [3,7,11,15,2,6,10,14,1,5,9,13,0,4,8,12]
            newBoard = origBoard[:]
            combines = 0
            combineSum = 0
            moveCount = 0
            movesMade = True
            while(movesMade):
                movesMade = False
                for cellIdx in range(12):
                    if newBoard[cellMap[cellIdx]] == 0:
                        for idx in range(3 - cellIdx/4):
                            if newBoard[cellMap[cellIdx+4+idx*4]] != 0:
                                newBoard[cellMap[cellIdx+idx*4]] = newBoard[cellMap[cellIdx+4+idx*4]]
                                newBoard[cellMap[cellIdx+4+idx*4]] = 0
                                movesMade = True
                                moveCount += 1
            for cellIdx in range(12):
                if newBoard[cellMap[cellIdx]] != 0 and newBoard[cellMap[cellIdx]] == newBoard[cellMap[cellIdx+4]]:
                    combines += 1
                    combineSum += origBoard[cellMap[cellIdx]] * 2
                    newBoard[cellMap[cellIdx]] *= 2
                    newBoard[cellMap[cellIdx+4]] = 0
                    for idx in range(2 - cellIdx/4):
                        newBoard[cellMap[cellIdx+4+idx*4]] = newBoard[cellMap[cellIdx+8+idx*4]]
                        newBoard[cellMap[cellIdx+8+idx*4]] = 0
            print(dir,"num combines", combines, "Sum", combineSum,"MoveCount", moveCount)
            if (bestCombines + bestMoveCount == 0 and combines + moveCount > 0) or \
                (bestCombineSum < combineSum) or \
                (bestMoveCount < moveCount and combineSum == bestCombineSum):
                bestCombines = combines
                bestDir = dir
                bestCombineSum = combineSum
                bestMoveCount = moveCount
                bestBoard = newBoard[:]

        print("Best Dir", bestDir)
        for i in range(len(bestBoard)):
            print('{:>6}'.format(bestBoard[i]),end='')
            if i % 4 == 3: print()

        return bestBoard, bestDir
