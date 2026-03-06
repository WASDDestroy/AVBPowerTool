import BaseUI
import os


class ConfigManagerUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "ConfigManagerUI"
        self.configManagerModule = self.myImporter.importModule(
            "ConfigManager.py")
        self.customizedFunction = {"S": "Set a config active",
                                   "P": "Save current config as a persistent one"}

    def callBackEnd(self, functionName: str):
        functionNameTuple = ("Config Library Manager",
                             "Set a config active",
                             "Save current config as a persistent one")
        self.myConfigManager = self.myImporter.createInstance(self.configManagerModule,
                                                              "ConfigManager",
                                                              self.myLogger)
        if functionName == functionNameTuple[0]:  # Manage
            self._inDevelopmentPlaceHolder()
        elif functionName == functionNameTuple[1]:
            configToActive = self. myUIUtils.selectConfigUI()
            if configToActive:
                self.myConfigManager.setConfigActive(configToActive)
            else:
                print("User cancelled operation.")
        elif functionName == functionNameTuple[2]:
            configName = input("Enter the name of your new config: ")
            result = self.myConfigManager.saveAsPersistentConfig(configName)
            if result:
                print("Success.")
            else:
                print("Failed.")
            self.myUIUtils.pressEnterToContinue()
