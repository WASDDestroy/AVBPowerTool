'''
ConfigManager provides useful functions for config management, including import, export and delete.
Batch operation are also supported.

Config files are placed in child folders of `Configs` and `key` folders.

This module will export zip files with flag file as exported config.

When using batch export, it will create a "super" zip that contains small zip packages.

:todo: reconstruct import part to avoid using CLI rename function.
'''

import os, zipfile, time, shutil
import LogUtils

class ConfigManager:

    TAG = "ConfigManager"

    def __init__(self, logger = None) -> None:
        if not logger:
            self.myLogger = LogUtils.LogUtils()
            self.myLogger.log("W", "Logger not given, created an instance just now.", "ConfigManager")
        else:
            self.myLogger = logger
        self.myLogger.log("I", "Instance of ConfigManager successfully created.", "ConfigManager")

    def saveAsPersistentConfig(self, configName) -> bool:
        if not self.__isConfigAvailable(configName):
            configName = self.__getNewConfigName()
        try:
            self.myLogger.log("I", "Creating config directory in Configs dir.", self.TAG)
            os.mkdir(os.path.join(os.getcwd(), "Configs", configName))
            self.myLogger.log("I", "Saving image info.", self.TAG)
            for i in os.listdir(os.path.join(os.getcwd(), "Core", "currentConfigs")):
                self.myLogger.log("I", "Filename: " + i, self.TAG)
                shutil.copy(os.path.join(os.getcwd(), "Core", "currentConfigs", i),
                            os.path.join(os.getcwd(), "Configs", configName, i))
            self.myLogger.log("I", "Creating key file directory in Keys dir.", self.TAG)
            os.mkdir(os.path.join(os.getcwd(), "Keys", configName))
            self.myLogger.log("I", "Saving public key file.", self.TAG)
            for i in os.listdir(os.path.join(os.getcwd(), "Core", "currentKeySet")):
                self.myLogger.log("I", "Filename: " + i, self.TAG)
                shutil.copy(os.path.join(os.getcwd(), "Core", "currentKeySet", i),
                            os.path.join(os.getcwd(), "Keys", configName, i))
            self.myLogger.log("I", "Config saved.", self.TAG)
            return True
        except Exception as e:
            self.myLogger.log("W", "Failed to save config: ", self.TAG)
            self.myLogger.log("W", str(e), self.TAG)
            return False

    def setConfigActive(self, configName) -> bool:
        try:
            self.setConfigDeactivate()
            for i in os.listdir(os.path.join(os.getcwd(), "Configs", configName)):
                shutil.copy(os.path.join(os.getcwd(), "Configs", configName, i),
                            os.path.join(os.getcwd(), "Core", "currentConfigs"))
            for i in os.listdir(os.path.join(os.getcwd(), "Keys", configName)):
                shutil.copy(os.path.join(os.getcwd(), "Keys", configName, i),
                            os.path.join(os.getcwd(), "Core", "currentKeySet"))
            return True
        except Exception as e:
            self.myLogger.log("W", "Failed to switch config " + configName + " active: ", self.TAG)
            self.myLogger.log("W", str(e), self.TAG)
            return False
    
    def setConfigDeactivate(self) -> bool:
        try:
            for i in os.listdir(os.path.join(os.getcwd(), "Core", "currentConfigs")):
                os.remove(os.path.join(os.getcwd(), "currentConfigs", i))
            for i in os.listdir(os.path.join(os.getcwd(), "Core", "currentKeySet")):
                os.remove(os.path.join(os.getcwd(), "Core", "currentKeySet", i))
            return True
        except Exception as e:
            self.myLogger.log("W", "Failed to deactivate current config: ", self.TAG)
            self.myLogger.log("W", str(e), self.TAG)
            return False
            

    def removeSingleConfig(self, configName) -> bool:
        try:
            shutil.rmtree(os.path.join(os.getcwd(), "Configs", configName))
            shutil.rmtree(os.path.join(os.getcwd(), "Keys", configName))
            return True
        except Exception as e:
            self.myLogger.log("W", "Failed to remove config: " + configName, self.TAG)
            self.myLogger.log("W", str(e), self.TAG)
            return False

    def checkConfigType(self, importFromDir = None, fileName = "myConfig.zip"):
        if importFromDir is None:
            importFromDir = os.getcwd()
        if fileName.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(importFromDir, fileName), 'r') as myZip:
                fileInfoList = myZip.infolist()
                isBatch = False
                isSingleConfig = False
                for i in fileInfoList:
                    if i.filename == "BATCH_CONFIG_AVBPOWERTOOL":
                        isBatch = True
                    elif i.filename == "this_is_a_config_file_of_avbpowertool":
                        isSingleConfig = True
                if isBatch and isSingleConfig:
                    return "INVALID"
                elif isBatch:
                    return "BATCH"
                elif isSingleConfig:
                    return "SINGLE"
                else:
                    return "INVALID"
        else:
            return "INVALID"
        
    def batchImportConfig(self, importFromDir = None, importFromFileName = "myBatchConfig.zip"):
        if importFromDir is None:
            importFromDir = os.getcwd()
        EXTRACT_ZIP_TO = os.path.join(os.getcwd(), "Core", "temp", "extractedConfigZips")
        if self.checkConfigType(importFromDir = importFromDir, fileName = importFromFileName) in ("INVALID", "SINGLE"):
            self.myLogger.log("W", "Attempting to import a invalid file %s from directory %s"%(importFromFileName, importFromDir), self.TAG)
            raise RuntimeError("Attempting to import a invalid file.")
        else:
            self.myLogger.log("I", "Valid single config %s from directory %s."%(importFromFileName, importFromDir), self.TAG)
        with zipfile.ZipFile(importFromDir + importFromFileName, 'r') as myZip:
            fileInfoList = myZip.infolist()
            fileNameList = []
            for i in fileInfoList:
                if i.filename != "BATCH_CONFIG_AVBPOWERTOOL":
                    fileNameList.append(i.filename)
            myZip.extractall(path = EXTRACT_ZIP_TO)
            configList = os.listdir(EXTRACT_ZIP_TO)
            os.remove(os.path.join(EXTRACT_ZIP_TO, "BATCH_CONFIG_AVBPOWERTOOL"))
            for i in configList:
                self.importSingleConfig(importFromDir = EXTRACT_ZIP_TO,
                                        importFromFileName = i)
            shutil.rmtree(EXTRACT_ZIP_TO)
    
    def batchExportConfig(self,
                          exportToDir = None,
                          exportToFileName = "myBatchConfig.zip",
                          selectedConfigs = ["current"]):
        if exportToDir is None:
            exportToDir = os.getcwd()
        SINGLE_CONFIG_EXPORT_TO = os.path.join(os.getcwd(), "Core", "temp", "exportSingleConfigZips")
        with zipfile.ZipFile(os.path.join(exportToDir, exportToFileName), 'w') as myZip:
            for i in selectedConfigs:
                self.exportSingleConfig(exportConfigFolderName = i,
                                        exportToDir = SINGLE_CONFIG_EXPORT_TO,
                                        exportToFileName = i + ".zip")
            for root, dirs, fileNames in os.walk(SINGLE_CONFIG_EXPORT_TO):
                for fileName in fileNames:
                    filePath = os.path.join(root, fileName)
                    arcName = os.path.relpath(filePath, os.path.dirname(i))
                    myZip.write(filePath, arcName)
                    self.myLogger.log("T", filePath, self.TAG)
            with open(os.path.join(SINGLE_CONFIG_EXPORT_TO, "BATCH_CONFIG_AVBPOWERTOOL"), "w") as myFile:
                myFile.write("Batch config of AVBPowerTool.")
            myZip.write(os.path.join(SINGLE_CONFIG_EXPORT_TO, "BATCH_CONFIG_AVBPOWERTOOL"))
        shutil.rmtree(SINGLE_CONFIG_EXPORT_TO)

    def importSingleConfig(self,
                           importFromDir = None,
                           importFromFileName = "myConfig.zip"):
        '''
        Import a *valid* config zip file.
        
        It will require a rename if flag file `RENAME_REQUIRED` is found in archive.

        :param importFromDir: Where should the method find config archive.
        :param importFromFileName: Which config file should the method use.
        :return: None
        '''
        if importFromDir is None:
            importFromDir = os.getcwd()
        EXTRACT_TO = os.path.join(os.getcwd(), "Core", "temp", "unZippedConfig")
        if self.checkConfigType(importFromDir = importFromDir, fileName = importFromFileName) != "SINGLE":
            self.myLogger.log("W", "Invalid single zip config file %s from directory %s"%(importFromFileName, importFromDir), self.TAG)
            raise RuntimeError("Invalid zip file!")
        else:
            self.myLogger.log("I", "Valid single config %s from directory %s."%(importFromFileName, importFromDir), self.TAG)
        with zipfile.ZipFile(os.path.join(importFromDir, importFromFileName), 'r') as myZip:
            fileInfoList = myZip.infolist()
            fileNameList = []
            renameBeforeImport = False
            for i in fileInfoList:
                if i.filename == "RENAME_REQUIRED":
                    renameBeforeImport = True
                elif i.filename == "this_is_a_config_file_of_avbpowertool":
                    pass
                else:
                    fileNameList.append(i.filename)
            configName = importFromFileName.strip(".zip")
            if renameBeforeImport:
                configName = self.__getNewConfigName()
            try:
                shutil.rmtree(EXTRACT_TO)
            except:
                pass
            myZip.extractall(path = EXTRACT_TO)
            try:
                os.remove(os.path.join(EXTRACT_TO, "RENAME_REQUIRED"))
                os.remove(os.path.join(EXTRACT_TO, "this_is_a_config_file_of_avbpowertool"))
            except Exception as e:
                self.myLogger.log("W", "Exception happened when deleting flag files: " + str(e), self.TAG)
                
            self.myLogger.log("T", "Successfully extracted config to temporary folder.", self.TAG)
            # default configs will be extracted to ./temp/unZippedConfig/currentConfigs
            # and ./temp/unZippedConfig/currentKeySet
            if renameBeforeImport:
                # rename one, copy one at once, and then remove.
                # config folder goes first.
                os.rename(os.path.join(EXTRACT_TO, "currentConfigs"),
                          os.path.join(EXTRACT_TO, configName))
                shutil.copytree(os.path.join(EXTRACT_TO, configName),
                                os.path.join(os.getcwd(), "Configs", configName))
                shutil.rmtree(os.path.join(EXTRACT_TO, configName))
                # then process keySet folder
                os.rename(os.path.join(EXTRACT_TO, "currentKeySet"),
                          os.path.join(EXTRACT_TO, configName))
                shutil.copytree(os.path.join(EXTRACT_TO, configName),
                                os.path.join(os.getcwd(), "Keys", configName))
                shutil.rmtree(os.path.join(EXTRACT_TO, configName))
            else:
                # check the availability of config name first
                if not self.__isConfigAvailable(configName):
                    # if not available, request a new config name.
                    # call to self.__getNewConfigName() should be avoided at frontend to avoid troubles when switching to GUI.
                    tmpFileName = os.listdir(os.path.join(EXTRACT_TO, "Configs"))[0]
                    configName = self.__getNewConfigName()
                    # rename one, copy one at once, and then remove.
                    # config folder goes first.
                    os.rename(os.path.join(EXTRACT_TO, "Configs", tmpFileName),
                            os.path.join(EXTRACT_TO, "Configs", configName))
                    shutil.copytree(os.path.join(EXTRACT_TO, "Configs", configName),
                                    os.path.join(os.getcwd(), "Configs", configName))
                    shutil.rmtree(os.path.join(EXTRACT_TO, "Configs", configName))
                    # then process keySet folder
                    os.rename(os.path.join(EXTRACT_TO, "Keys", tmpFileName),
                            os.path.join(EXTRACT_TO, "Keys", configName))
                    shutil.copytree(os.path.join(EXTRACT_TO, "Keys", configName),
                                    os.path.join(os.getcwd(), "Keys", configName))
                    shutil.rmtree(os.path.join(EXTRACT_TO, "Keys", configName))
                else:
                    # if available, copy them directly.
                    # we should keep this control flow only in the final version.
                    shutil.copytree(os.path.join(EXTRACT_TO, "Configs", configName),
                                    os.path.join(os.getcwd(), "Configs", configName))
                    shutil.rmtree(os.path.join(EXTRACT_TO, "Configs", configName))
                    shutil.copytree(os.path.join(EXTRACT_TO, "Keys", configName),
                                    os.path.join(os.getcwd(), "Keys", configName))
                    shutil.rmtree(os.path.join(EXTRACT_TO, "Keys", configName))
            self.myLogger.log("T", "Successfully copied config to target folder.", self.TAG)
        shutil.rmtree(EXTRACT_TO)
        self.myLogger.log("T", "Successfully removed temp folder.", self.TAG)

    def __isConfigAvailable(self, configName : str):
        '''
        __isConfigAvailable checks name of configs to avoid overriding existing files.
        
        :param configName: the name of your config.
        :return: True when config name available, False when config name is taken by another existing config.
        '''
        configNameInUse = ["currentConfigs", "current"]
        for folderName in os.listdir(os.path.join(os.getcwd(), "Configs")):
            configNameInUse.append(folderName)
        return not configName in configNameInUse

    def __getNewConfigName(self):
        '''
        Private method to get a new config name when rename is required during import.
        
        Will let user type another name when attempting to use name `currentConfigs` and provide a autogenerated name after 3 unsuccessful attempts.

        :return: Config name string
        '''
        print("To avoid overriding existing files, please provide another config name to continue import process.")
        count = 0
        while count < 3:
            newConfigName = input("New config name: ")
            if self.__isConfigAvailable(newConfigName) and len(newConfigName) > 0:
                return newConfigName
            else:
                print("Illegal config name, try another name instead.")
                count += 1
        else:
            newConfigName = "AutoRenamedConfig_" + time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
            print("Using a autogenerated config name to complete import: " + newConfigName)
            return newConfigName

    def exportSingleConfig(self,
                           exportConfigFolderName = "current",
                           exportToDir = None,
                           exportToFileName = None) -> bool:
        """
        Export a single config as a zip file (with *valid* flag) to the directory you assigned.
        
        In the archive exported you will find a file named `this_is_a_config_file_of_avbpowertool`, which indicates the validity of this file.
        
        If you decided to let this method export the config that is used currently, it will additionally add a flag file named `RENAME_REQUIRED` to tell the program that we need a rename before importing it to avoid overriding config.
        (recommended to let users rename it before exporting in order to avoid forgetting the use of this config.)

        :param exportConfigFolderName: Determine which config folder you want to export. Set to `current` (case-sensitive) or ignore it will use folder `currentConfigs`.
        :param exportToDir: Determine where you want to save the exported zip file, keep it empty if you want to save it to the project's **root** folder.
        :param exportToFileName: Determine the filename of zip file, default value is `myConfig.zip`
        :return: bool
        :raise FileNotFoundError: Config folder assigned not exist.
        """
        if exportToDir is None:
            exportToDir = os.getcwd()
        if exportConfigFolderName == "current":
            foldersRequired = (os.path.join(os.getcwd(), "Core", "currentConfigs"),
                               os.path.join(os.getcwd(), "Core", "currentKeySet"))
        else:
            foldersRequired = (os.path.join(os.getcwd(), "Configs", exportConfigFolderName),
                               os.path.join(os.getcwd(), "Keys", exportConfigFolderName))
        folderNameInArchive = ("Configs", "Keys")
        if exportToFileName == None:
            exportToFileName = exportConfigFolderName + ".zip"
            self.myLogger.log("W", "Use default file name " + exportToFileName, self.TAG)
        
        if not exportToFileName.endswith(".zip"):
            self.myLogger.log("W", "Attempting to use other file extension name while exporting config.", self.TAG)
        if not os.path.exists(foldersRequired[0]):
            self.myLogger.log("W", "Unable to find folder " + foldersRequired[0], self.TAG)
            raise FileNotFoundError("Assigning a config folder that does not exist.")
        if not os.path.exists(foldersRequired[1]):
            self.myLogger.log("W", "Unable to find folder " + foldersRequired[1], self.TAG)
            raise FileNotFoundError("Assigning a config folder that does not exist.")
        

        with zipfile.ZipFile(os.path.join(exportToDir, exportToFileName), 'w') as myZip:
            try:
                for i in range(len(foldersRequired)):
                    for fileName in os.listdir(foldersRequired[i]):
                        filePath = os.path.join(foldersRequired[i], fileName)
                        arcName = os.path.join(folderNameInArchive[i], exportConfigFolderName, fileName)
                        myZip.write(filePath, arcName)
                        self.myLogger.log("T", "File path: " + filePath, self.TAG)
                        self.myLogger.log("T", "Arcname: " + arcName, self.TAG)
            except Exception as e:
                self.myLogger.log("E", "Exception happened when exporting config: " + str(e), self.TAG)
            with open("this_is_a_config_file_of_avbpowertool", "w") as myTempFile:
                myTempFile.write("This is a file that indicates the zip archive is a valid config file of AVBPowerTool.")
            myZip.write("this_is_a_config_file_of_avbpowertool")
            os.remove("this_is_a_config_file_of_avbpowertool")
            if exportConfigFolderName == "current":
                with open("RENAME_REQUIRED", "w") as myTempFile:
                    myTempFile.write("Please rename this config before import.")
                myZip.write("RENAME_REQUIRED")
                os.remove("RENAME_REQUIRED")
        return True
    
    def getAllConfigs(self, configDir = None):
        if configDir is None:
            configDir = os.path.join(os.getcwd(), "Configs")
        configList = []
        for i in os.listdir(configDir):
            configList.append(i)
        return configList

if __name__ == "__main__":
    myConfigManager = ConfigManager()
    myConfigManager.importSingleConfig()