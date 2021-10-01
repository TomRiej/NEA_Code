# reward for speed and num checkpoints passed/ laps completed
from QTable import QTable
from random import random

class QAgent:
    def __init__(self, params):
        self.__LEARNING_RATE = params["learningRate"]                   # doesnt change throughout training
        self.__DISCOUNT_FACTOR = params["discountFactor"]               # ^
        self.__probabilityToExplore = params["probabilityToExplore"]    # decreases throughout training
        
        self.__totalReward = 0.0
        self.__successfulTrainingIterations = 0
        
        # error raised if invalid input is handled by external script calling this class
        self.__qTable = QTable(params["stateShape"],
                               params["actionShape"])
        
    def decideAction(self, state):
        if not self.__qTable.checkStateIsValid(state):
            return None
        if random() < self.__probabilityToExplore:
            return self.__qTable.getRandomAction()
        else:
            return self.__qTable.getActionWithMaxQValue(state)
    
    def calcInstantReward(self, speed, lapsCompleted, carHasDeslotted): # need to pass in car data, so called separatelly to trian
        if carHasDeslotted:
            return - 1000000
        return (speed*0.1) + (lapsCompleted*10) 
    
    def train(self, curState, nextState, action, instantReward):
        # validate all states
        if not (self.__qTable.checkStateIsValid(curState) and 
                self.__qTable.checkStateIsValid(nextState) and 
                self.__qTable.checkActionIsValid(action)):
            return False
        # calculating new QValue
        oldValue = (1-self.__LEARNING_RATE) * self.__qTable.getQValue(curState, action)
        discountedOptimalFutureReward = self.__DISCOUNT_FACTOR * self.__qTable.getMaxQValueOfState(nextState)
        learnedValue = instantReward + discountedOptimalFutureReward
        newQValue = oldValue + (self.__LEARNING_RATE * learnedValue)
        # updating the table
        self.__qTable.updateAt(curState, action, newQValue)
        self.__successfulTrainingIterations += 1
        print("training iteration:", self.__successfulTrainingIterations)
        self.reduceProbToExplore()
        return True

    def reduceProbToExplore(self):
        self.__probabilityToExplore *= 0.9999
        print("new prob to explore = ", self.__probabilityToExplore)
        
    def writeTable(self):
        self.__qTable.writeQTableToFile()
        
        
        
if __name__=='__main__':
    from random import randint
    DEBUG = False
    params = {"learningRate": 0.5,
              "discountFactor": 0.05,
              "probabilityToExplore": 1,
              "stateShape": [[0, 0, 0], [1, 99, 999], [1, 30, 100]],
              "actionShape": [30,        90,           5]}
    
    qAgent = QAgent(params)
    qAgent.writeTable()
    
    laps = 0
    s1 = "{:06d}".format(randint(int("000000"), int("199999")))
    desisions = 0
    if DEBUG:
        print(s1)
    for i in range(200000):
        # print()
        # get action
        act = qAgent.decideAction(s1)
        spd = int(act)*10
        if DEBUG:
            print(spd)
        if spd == 0:
            s2 = list(s1)
            for i in range(5, 2, -1):
                s2[i] = '0'
            s2 = "".join(s2)
            if DEBUG:
                print(s2)
        elif spd > int(s1[-3:]):
            if DEBUG:
                print("higher")
            s2 = list(s1)
            newDist = int(s2[1] + s2[2]) - randint(5,30)
            if newDist < 0:
                newDist = randint(40,99)
                s2[0] = str(randint(0,1))
            newDist = f"{newDist:02d}"
            s2[1], s2[2] = list(newDist)
            newSpd = int("".join(s2[-3:])) + randint(100,300)
            if newSpd > 999:
                newSpd = 999
            for i in range(3):
                s2[i+3] = str(newSpd)[i]
            s2 = "".join(s2)
            desisions += 1
            if DEBUG:
                print(s2)
        else:
            if DEBUG:
                print("lower")
            s2 = list(s1)
            newDist = int(s2[1] + s2[2]) - randint(5,30)
            if newDist < 0:
                newDist = randint(40,99)
                s2[0] = str(randint(0,1))
            newDist = f"{newDist:02d}"
            s2[1], s2[2] = list(newDist)
            newSpd = int("".join(s2[-3:])) - randint(100,200)
            if newSpd < 0:
                newSpd = 0
            for i in range(3):
                s2[i+3] = f"{newSpd:03d}"[i]
            s2 = "".join(s2)
            desisions += 1
            if DEBUG:
                print(s2)
            
        if desisions % 6 == 0:
            if DEBUG:
                print("lap passed")
            laps += 1
            desisions = 0
        if desisions % 20000 == 0:
            qAgent.reduceProbToExplore()
            
        deslot = False
        s = int(s2[3:])
        if s > 800:#random() < int(s2[3:]) / 2000:
            if DEBUG:
                print("deslot")
            deslot = True
        elif s > 700 and random() < 0.4:
            deslot = True
        
        instReward = qAgent.calcInstantReward(int(s2[3:]), laps, deslot)
        qAgent.train(s1, s2, act, instReward)
       
        s1 = s2
    qAgent.writeTable()
    print("done")
        
        # deslot = False
        # if random() < int(s2) / 200000:
        #     if random() < spd / 100:
        #         deslot = True
        
        # qAgent.calcInstantReward()
        
        