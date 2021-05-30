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
