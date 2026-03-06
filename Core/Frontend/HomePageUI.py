import Core.Frontend.BaseUI as BaseUI


class HomePageUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "HomePageUI"
        self.customizedFunction = {
            "V": "View current config info"
        }
        self.DisplayAVBInfo = self.myImporter.importModule("DisplayAVBInfo")

    def callBackEnd(self, functionName: str):
        if functionName == "View current config info":
            self.DisplayAVBInfo.entry(self.myLogger)  # type: ignore


if __name__ == "__main__":
    myHomePage = HomePageUI()
    while 1:
        myHomePage.entry()
