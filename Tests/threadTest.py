from threading import Thread
from time import sleep

class MyThread:
    def __init__(self) -> None:
        self.thread = Thread(target=self.doSomething)
        self.continueRunning = True
        
    def stopThread(self):
        self.continueRunning = False
        
    def doSomething(self):
        sleep(1)
        print("slept 1...")
        if self.continueRunning:
            self.doSomething()
        else:
            print("sleep for shutdown")
            sleep(1)
            return
            
    def stop(self):
        self.stopThread()
        self.thread.join()
        
    def start(self):
        self.thread.start()
        
        
if __name__ == '__main__':
    t = MyThread()
    t.start()
    sleep(10)
    t.stop()