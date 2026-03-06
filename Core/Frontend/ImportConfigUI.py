import BaseUI
import ConfigManager
import os


class ImportConfigUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "ImportConfigUI"
        self.customizedFunction = {"A": "Import all configs under root folder",
                                   "S": "Import selected config(s) under specified folder", }
        self.myConfigManager = ConfigManager.ConfigManager(
            logger=self.myLogger)

    def callBackEnd(self, functionName: str):
        if functionName == self.customizedFunction["A"]:
            self.__handleImportLogic()
        elif functionName == self.customizedFunction["S"]:
            self._inDevelopmentPlaceHolder()

    def __handleImportLogic(self):
        importFileName = self.myUIUtils.selectFileUI()
        if importFileName is None:
            print("Cancelled.")
            return
        archiveType = self.myConfigManager.checkConfigType(
            fileName=importFileName)
        if archiveType == "SINGLE":
            try:
                self.myConfigManager.importSingleConfig(
                    importFromFileName=importFileName)
                print("Successfully imported config.")
            except Exception as e:
                self.myLogger.log("W", e, self.TAG)
                print("Import failed!")
            self.myUIUtils.pressEnterToContinue()
        elif archiveType == "BATCH":
            try:
                self.myConfigManager.batchImportConfig(
                    importFromFileName=importFileName)
                print("Successfully imported config.")
            except Exception as e:
                self.myLogger.log("W", e, self.TAG)
                print("Import failed!")
            self.myUIUtils.pressEnterToContinue()
        else:
            print("Invalid archive file.")
            self.myUIUtils.pressEnterToContinue()
