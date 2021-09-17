from QAgent import QAgent


# class Board:
#     def __init__(self, size):   
#         self.__board = [["-" for x in range(5)] for y in range(5)]
#         self.__agentX = 0
#         self.__agentY = 0
#         self.__board[self.__agentY][self.__agentX] = "x"   # agent
#         self.__board[-1][-1] = "G" #goal
#         self.__board[3][2] = "B" #bad guy
#         self.__board[1][2] = "B" 
        
#     def move(self, move):
#         self.__board[self.__agentY][self.__agentX] = "-"
#         if move == 0:
#             self.__agentX += 1 # move right
#         elif move == 1:
#             self.__agentX -= 1 # move left
#         elif move == 2:
#             self.__agentY += 1 # move down
#         else:
#             self.__agentY -= 1 # move up
#         self.__board[self.__agentY][self.__agentX] = "x"
            

#     def printBoard(self):
#         for row in self.__board:
#             print(row)
            
            
# board = Board(5)

params = {"stateRange": [0,5],
          "actionRange": [0,5],
          "stateGroupSize": 1,
          "actionGroupSize": 1,
          "learningRate": 1.0,
          "discountFactor": 0.0,
          "probabilityToExplore": 0.1}

agent = QAgent(**params)



# = random code

# def __learnTrackLocations(self):
    #     startTime = time()
    #     trackLocationsFound = False
    #     trackLocationData = []
    #     while not trackLocationsFound and time()-startTime < VALIDATION_TIMEOUT:
    #         carInfo = self.__camera.getCarInfo(ZOOM_DEPTH,
    #                                            ZOOM_PERCENTAGE)
    #         trackLocationData.append(carInfo["nextTrackLoc"])
    #         if len(trackLocationData) > 10:
    #             if trackLocationData[0] == trackLocationData[-2] == trackLocationData[-1]:
    #                 trackLocationsFound, trackLocationOrder = self.__deduceTrackLocationOrder(trackLocationData)
        
    #     if trackLocationsFound:
    #         self.__trackLocationOrder = trackLocationOrder
    #         print(f"track Location order determined: {trackLocationOrder} ")
    #     else:
    #         print("failed to learn track location order")
    #         self.__endProgram()
            
    # def __deduceTrackLocationOrder(self, trackLocationData):
    #     finalTrackLocationOrder = []
    #     for i, loc in enumerate(trackLocationData[:-1]):
    #         if loc == trackLocationData[i+1] and loc not in finalTrackLocationOrder:
    #             finalTrackLocationOrder.append(loc)
    #     return (len(finalTrackLocationOrder) == NUM_TRACK_LOCATIONS), finalTrackLocationOrder        
            
    # def __checkNextTrackLocIsValid(self, predictedTrackLoc):
    #     print("predicted", predictedTrackLoc)
    #     if self.__curClosestTrackLoc is None:
    #         self.__curClosestTrackLoc = predictedTrackLoc
    #         return True
    #     elif predictedTrackLoc == self.__curClosestTrackLoc:
    #         print("track Location the same")
    #         return True
    #     nextLocIndex = self.__trackLocationOrder.index(self.__curClosestTrackLoc) + 1
    #     if nextLocIndex >= len(self.__trackLocationOrder):
    #         nextLocIndex = 0
    #     print(nextLocIndex)
    #     nextPossibleTrackLoc = self.__trackLocationOrder[nextLocIndex]
    #     print("next: ", nextPossibleTrackLoc)
    #     if predictedTrackLoc == nextPossibleTrackLoc:
    #         self.__curClosestTrackLoc = predictedTrackLoc
    #         return True
    #     else:
    #         return False
