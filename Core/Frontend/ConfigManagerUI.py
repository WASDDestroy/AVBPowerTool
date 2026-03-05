import BaseUI
import os

class ConfigManagerUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "ConfigManagerUI"
        self.configManagerModule = self._importModule("ConfigManager.py")
        self.customizedFunction = {"S" : "Set a config active",
                                   "P" : "Save current config as a persistent one"}

    def callBackEnd(self, functionName: str):
        functionNameTuple = ("Config Library Manager",
                             "Set a config active",
                             "Save current config as a persistent one")
        self.myConfigManager = self._createInstance(self.configManagerModule,
                                                    "ConfigManager",
                                                    self.myLogger)
        if functionName == functionNameTuple[0]: # Manage
            print("Function is in development.")
            self._pressEnterToContinue()
        elif functionName == functionNameTuple[1]:
            configToActive = self.__setConfigActiveUI()
            if configToActive:
                self.myConfigManager.setConfigActive(configToActive)
            else:
                print("User cancelled operation.")
        elif functionName == functionNameTuple[2]:
            configName = input("Enter the name of your new config.")
            result = self.myConfigManager.saveAsPersistentConfig(configName)
            if result:
                print("Success.")
            else:
                print("Failed.")
            self._pressEnterToContinue()
        else:
            print("Invalid choice.")
            self._pressEnterToContinue()

    def __setConfigActiveUI(self):
        configNames = self.myConfigManager.getAllConfigs()
        for i in range(len(configNames)):
            print(i + 1, configNames[i])
        print("Select a config with number. Enter -1 to cancel.")
        while 1:
            myInput = input("Your choice: ")
            try:
                inputNumber = int(myInput)
                if 0 < inputNumber <= len(configNames):
                    print("Import file: %s"%(configNames[inputNumber - 1]))
                    break
                elif inputNumber == -1:
                    return None
                else:
                    raise IndexError
            except Exception as e:
                print("Invalid input, try again.")
                self.myLogger.log("W", "Invalid input when determining config to active: " + repr(e), self.TAG)
        print("Set this config active? [y/N]", end = " ")
        if input().upper() == "Y":
            return configNames[inputNumber - 1]
        else:
            return None