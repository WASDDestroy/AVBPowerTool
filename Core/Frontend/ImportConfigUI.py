import BaseUI
import ConfigManager
import os

class ImportConfigUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "ImportConfigUI"
        self.customizedFunction = {"A" : "Import all configs under root folder",
                                   "S" : "Import selected config(s) under specified folder",}
        self.myConfigManager = ConfigManager.ConfigManager(logger=self.myLogger)
    
    def callBackEnd(self, functionName: str):
        if functionName == self.customizedFunction["A"]:
            self.__handleImportLogic()
        elif functionName == self.customizedFunction["S"]:
            self._inDevelopmentPlaceHolder()
    
    def __handleImportLogic(self):
        importFileName = self.__selectFileUI()
        if importFileName is None:
            print("Cancelled.")
            return
        archiveType = self.myConfigManager.checkConfigType(fileName = importFileName)
        if archiveType == "SINGLE":
            try:
                self.myConfigManager.importSingleConfig(importFromFileName = importFileName)
                print("Successfully imported config.")
            except Exception as e:
                self.myLogger.log("W", e, self.TAG)
                print("Import failed!")
            self._pressEnterToContinue()
        elif archiveType == "BATCH":
            try:
                self.myConfigManager.batchImportConfig(importFromFileName = importFileName)
                print("Successfully imported config.")
            except Exception as e:
                self.myLogger.log("W", e, self.TAG)
                print("Import failed!")
            self._pressEnterToContinue()
        else:
            print("Invalid archive file.")
            self._pressEnterToContinue()

    def __selectFileUI(self, extensionName = ".zip"):
        """
        Provide filename of zip archive selected. Will return None if user cancels.
        """
        print("Place zip file under root directory and press Enter to continue.")
        self._pressEnterToContinue()
        rootDir = os.getcwd()
        fileCanBeSelected = []
        for i in os.listdir(rootDir):
            if i.endswith(extensionName):
                fileCanBeSelected.append(i)
        for i in range(len(fileCanBeSelected)):
            print(i + 1, fileCanBeSelected[i])
        print("Select a file with number. Enter -1 to cancel.")
        while 1:
            myInput = input("Your choice: ")
            try:
                inputNumber = int(myInput)
                if 0 < inputNumber <= len(fileCanBeSelected):
                    print("Select file: %s"%(fileCanBeSelected[inputNumber - 1]))
                    break
                elif inputNumber == -1:
                    return None
                else:
                    raise IndexError
            except Exception as e:
                print("Invalid input, try again.")
                self.myLogger.log("W", "Invalid input when selecting file: " + repr(e), self.TAG)
        if self.confirmOperation(prompt = "Select this file?"):
            return fileCanBeSelected[inputNumber - 1]
        else:
            return None