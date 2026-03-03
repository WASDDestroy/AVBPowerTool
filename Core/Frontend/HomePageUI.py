import BaseUI

class HomePageUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.customizedFunction = {
            "V" : "View current config info"
        }
        self.DisplayAVBInfo = self._importModule("DisplayAVBInfo")
        self.TAG = "HomePageUI"
    
    def callBackEnd(self, functionName: str):
        self.handleBackAndExit(functionName)
        if functionName == "View current config info":
            self.DisplayAVBInfo.entry()

if __name__ == "__main__":
    myHomePage = HomePageUI()
    while 1:
        myHomePage.entry()
