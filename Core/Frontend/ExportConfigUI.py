import BaseUI
import os
import ConfigManagerUI


class ExportConfigUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "ExportConfigUI"
        self.customizedFunction = {
            "E": "Export a selected config",
            "A": "Batch export configs as an archive",
            "S": "Batch export configs as single archives",
        }
        self.myConfigManager = self.myImporter.createInstance(self.myImporter.importModule("ConfigManager"),
                                                              "ConfigManager",
                                                              self.myLogger)

    def callBackEnd(self, functionName: str):
        if functionName == self.customizedFunction["E"]:
            self.__handleSingleExportLogic()
        elif functionName == self.customizedFunction["A"]:
            self._inDevelopmentPlaceHolder()
        elif functionName == self.customizedFunction["S"]:
            self._inDevelopmentPlaceHolder()

    def __handleSingleExportLogic(self):
        configName = self.myUIUtils.selectConfigUI()
        if configName is None:
            print("User cancelled operation.")
        else:
            try:
                result = self.myConfigManager.exportSingleConfig(
                    exportConfigFolderName=configName)
                if result:
                    print("Successfully exported selected config %s to root directory as an archive." % (
                        configName))
                else:
                    print("Failed to export config!")
            except FileNotFoundError:
                print("Config folder not found!")
                self.myLogger.log("W",
                                  "Config folder not found! Check system settings because config is already guaranteed exist in previous steps.",
                                  self.TAG)
        self.myUIUtils.pressEnterToContinue()
