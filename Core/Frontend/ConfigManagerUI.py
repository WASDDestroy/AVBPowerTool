import BaseUI
import os

class ConfigManagerUI(BaseUI.BaseUI):

    def customizedInit(self):
        self.TAG = "ConfigManagerUI"
        self.configManagerModule = self._importModule("ConfigManager.py")
        self.customizedFunction = {"S" : "Set a config active",
                                   "P" : "Save current config as a persistent one"}

    def callBackEnd(self, functionName: str):
        functionNameTuple = ("Import Config",
                             "Export Config",
                             "Config Library Manager",
                             "Set a config active",
                             "Save current config as a persistent one")
        self.myConfigManager = self._createInstance(self.configManagerModule,
                                                    "ConfigManager",
                                                    self.myLogger)
        if functionName == functionNameTuple[0]:
            importFileName = self.__importConfigFromFileUI()
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
        elif functionName == functionNameTuple[1]:
            print("Function is in development.")
            self._pressEnterToContinue()
        elif functionName == functionNameTuple[2]:
            print("Function is in development.")
            self._pressEnterToContinue()
        elif functionName == functionNameTuple[3]:
            configToActive = self.__setConfigActiveUI()
            if configToActive:
                self.myConfigManager.setConfigActive(configToActive)
            else:
                print("User cancelled operation.")
        elif functionName == functionNameTuple[4]:
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

    def __importConfigFromFileUI(self):
        """
        Provide filename of zip archive to be imported. Will return None if user cancels.
        """
        print("Place zip file under root directory and press Enter to continue.")
        self._pressEnterToContinue()
        rootDir = os.getcwd()
        fileCanBeImported = []
        for i in os.listdir(rootDir):
            if i.endswith(".zip"):
                fileCanBeImported.append(i)
        for i in range(len(fileCanBeImported)):
            print(i + 1, fileCanBeImported[i])
        print("Select a file to import with number. Enter -1 to cancel.")
        while 1:
            myInput = input("Your choice: ")
            try:
                inputNumber = int(myInput)
                if 0 < inputNumber <= len(fileCanBeImported):
                    print("Import file: %s"%(fileCanBeImported[inputNumber - 1]))
                    break
                elif inputNumber == -1:
                    return None
                else:
                    raise IndexError
            except Exception as e:
                print("Invalid input, try again.")
                self.myLogger.log("W", "Invalid input when determining config to import: " + repr(e), self.TAG)
        print("Import this file? [y/N]", end = " ")
        if input().upper() == "Y":
            return fileCanBeImported[inputNumber - 1]
        else:
            return None