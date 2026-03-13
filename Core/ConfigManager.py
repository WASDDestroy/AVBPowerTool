"""
ConfigManager provides useful functions for config management, including import, export and delete.
Batch operation are also supported.

Config files are placed in child folders of `Configs` and `key` folders.

This module will export zip files with flag file as exported config.

When using batch export, it will create a "super" zip that contains small zip packages.

:todo: reconstruct import part to avoid using CLI rename function.
"""

import os, zipfile, time, shutil
import Core.LogUtils as LogUtils

class ConfigManager:

    TAG = "ConfigManager"

    def __init__(self, logger = None) -> None:
        if not logger:
            self.myLogger = LogUtils.LogUtils()
            self.myLogger.log("W", "Logger not given, created an instance just now.", "ConfigManager")
        else:
            self.myLogger = logger
        self.myLogger.log("I", "Instance of ConfigManager successfully created.", "ConfigManager")

    def save_as_persistent_config(self, config_name) -> bool:
        if not self.__is_config_available(config_name):
            config_name = self.__get_new_config_name()
        try:
            self.myLogger.log("I", "Creating config directory in Configs dir.", self.TAG)
            os.mkdir(os.path.join(os.getcwd(), "Configs", config_name))
            self.myLogger.log("I", "Saving image info.", self.TAG)
            for i in os.listdir(os.path.join(os.getcwd(), "Core", "currentConfigs")):
                self.myLogger.log("I", "Filename: " + i, self.TAG)
                shutil.copy(os.path.join(os.getcwd(), "Core", "currentConfigs", i),
                            os.path.join(os.getcwd(), "Configs", config_name, i))
            self.myLogger.log("I", "Creating key file directory in Keys dir.", self.TAG)
            os.mkdir(os.path.join(os.getcwd(), "Keys", config_name))
            self.myLogger.log("I", "Saving public key file.", self.TAG)
            for i in os.listdir(os.path.join(os.getcwd(), "Core", "currentKeySet")):
                self.myLogger.log("I", "Filename: " + i, self.TAG)
                shutil.copy(os.path.join(os.getcwd(), "Core", "currentKeySet", i),
                            os.path.join(os.getcwd(), "Keys", config_name, i))
            self.myLogger.log("I", "Config saved.", self.TAG)
            return True
        except Exception as e:
            self.myLogger.log("W", "Failed to save config: ", self.TAG)
            self.myLogger.log("W", str(e), self.TAG)
            return False

    def set_config_active(self, config_name) -> bool:
        try:
            self.set_config_deactivate()
            for i in os.listdir(os.path.join(os.getcwd(), "Configs", config_name)):
                shutil.copy(os.path.join(os.getcwd(), "Configs", config_name, i),
                            os.path.join(os.getcwd(), "Core", "currentConfigs"))
            for i in os.listdir(os.path.join(os.getcwd(), "Keys", config_name)):
                shutil.copy(os.path.join(os.getcwd(), "Keys", config_name, i),
                            os.path.join(os.getcwd(), "Core", "currentKeySet"))
            return True
        except Exception as e:
            self.myLogger.log("W", "Failed to switch config " + config_name + " active: ", self.TAG)
            self.myLogger.log("W", str(e), self.TAG)
            return False
    
    def set_config_deactivate(self) -> bool:
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
            

    def remove_single_config(self, config_name) -> bool:
        try:
            shutil.rmtree(os.path.join(os.getcwd(), "Configs", config_name))
            shutil.rmtree(os.path.join(os.getcwd(), "Keys", config_name))
            return True
        except Exception as e:
            self.myLogger.log("W", "Failed to remove config: " + config_name, self.TAG)
            self.myLogger.log("W", str(e), self.TAG)
            return False

    @staticmethod
    def check_config_type(import_from_dir = None, file_name ="myConfig.zip"):
        if import_from_dir is None:
            import_from_dir = os.getcwd()
        if file_name.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(import_from_dir, file_name), 'r') as myZip:
                file_info_list = myZip.infolist()
                is_batch = False
                is_single_config = False
                for i in file_info_list:
                    if i.filename == "BATCH_CONFIG_AVBPOWERTOOL":
                        is_batch = True
                    elif i.filename == "this_is_a_config_file_of_avbpowertool":
                        is_single_config = True
                if is_batch and is_single_config:
                    return "INVALID"
                elif is_batch:
                    return "BATCH"
                elif is_single_config:
                    return "SINGLE"
                else:
                    return "INVALID"
        else:
            return "INVALID"
        
    def batch_import_config(self, import_from_dir = None, import_from_file_name ="myBatchConfig.zip"):
        if import_from_dir is None:
            import_from_dir = os.getcwd()
        extract_zip_to = os.path.join(os.getcwd(), "Core", "temp", "extractedConfigZips")
        if self.check_config_type(import_from_dir= import_from_dir, file_name= import_from_file_name) in ("INVALID", "SINGLE"):
            self.myLogger.log("W", "Attempting to import a invalid file %s from directory %s" % (import_from_file_name, import_from_dir), self.TAG)
            raise RuntimeError("Attempting to import a invalid file.")
        else:
            self.myLogger.log("I", "Valid single config %s from directory %s." % (import_from_file_name, import_from_dir), self.TAG)
        with zipfile.ZipFile(import_from_dir + import_from_file_name, 'r') as myZip:
            file_info_list = myZip.infolist()
            file_name_list = []
            for i in file_info_list:
                if i.filename != "BATCH_CONFIG_AVBPOWERTOOL":
                    file_name_list.append(i.filename)
            myZip.extractall(path = extract_zip_to)
            config_list = os.listdir(extract_zip_to)
            os.remove(os.path.join(extract_zip_to, "BATCH_CONFIG_AVBPOWERTOOL"))
            for i in config_list:
                self.import_single_config(import_from_dir= extract_zip_to,
                                          import_from_file_name= i)
            shutil.rmtree(extract_zip_to)
    
    def batch_export_config(self,
                            export_to_dir = None,
                            export_to_file_name ="myBatchConfig.zip",
                            selected_configs=None):
        if selected_configs is None:
            selected_configs = ["current"]
        if export_to_dir is None:
            export_to_dir = os.getcwd()
        single_config_export_to = os.path.join(os.getcwd(), "Core", "temp", "exportSingleConfigZips")
        with zipfile.ZipFile(os.path.join(export_to_dir, export_to_file_name), 'w') as myZip:
            for i in selected_configs:
                self.export_single_config(export_config_folder_name= i,
                                          export_to_dir= single_config_export_to,
                                          export_to_file_name=i + ".zip")
            for root, dirs, fileNames in os.walk(single_config_export_to):
                for fileName in fileNames:
                    file_path = os.path.join(root, fileName)
                    arc_name = os.path.relpath(file_path, os.path.dirname(i))
                    myZip.write(file_path, arc_name)
                    self.myLogger.log("T", file_path, self.TAG)
            with open(os.path.join(single_config_export_to, "BATCH_CONFIG_AVBPOWERTOOL"), "w") as myFile:
                myFile.write("Batch config of AVBPowerTool.")
            myZip.write(os.path.join(single_config_export_to, "BATCH_CONFIG_AVBPOWERTOOL"))
        shutil.rmtree(single_config_export_to)

    def import_single_config(self,
                             import_from_dir = None,
                             import_from_file_name ="myConfig.zip"):
        """
        Import a *valid* config zip file.

        It will require a rename if flag file `RENAME_REQUIRED` is found in archive.

        :param import_from_dir: Where should the method find config archive.
        :param import_from_file_name: Which config file should the method use.
        :return: None
        """
        if import_from_dir is None:
            import_from_dir = os.getcwd()
        extract_to = os.path.join(os.getcwd(), "Core", "temp", "unZippedConfig")
        if self.check_config_type(import_from_dir= import_from_dir, file_name= import_from_file_name) != "SINGLE":
            self.myLogger.log("W", "Invalid single zip config file %s from directory %s" % (import_from_file_name, import_from_dir), self.TAG)
            raise RuntimeError("Invalid zip file!")
        else:
            self.myLogger.log("I", "Valid single config %s from directory %s." % (import_from_file_name, import_from_dir), self.TAG)
        with zipfile.ZipFile(os.path.join(import_from_dir, import_from_file_name), 'r') as myZip:
            file_info_list = myZip.infolist()
            file_name_list = []
            rename_before_import = False
            for i in file_info_list:
                if i.filename == "RENAME_REQUIRED":
                    rename_before_import = True
                elif i.filename == "this_is_a_config_file_of_avbpowertool":
                    pass
                else:
                    file_name_list.append(i.filename)
            config_name = import_from_file_name.rstrip(".zip")
            rename_before_import = rename_before_import or not self.__is_config_available(config_name)
            if rename_before_import:
                config_name = self.__get_new_config_name()
            shutil.rmtree(extract_to, ignore_errors=True)
            myZip.extractall(path = extract_to)
            try:
                os.remove(os.path.join(extract_to, "RENAME_REQUIRED"))
            except Exception as e:
                self.myLogger.log("W", "Exception happened when deleting flag files: " + str(e), self.TAG)
            try:
                os.remove(os.path.join(extract_to, "this_is_a_config_file_of_avbpowertool"))
            except Exception as e:
                self.myLogger.log("W", "Exception happened when deleting flag files: " + str(e), self.TAG)
                
            self.myLogger.log("T", "Successfully extracted config to temporary folder.", self.TAG)
            shutil.copytree(os.path.join(extract_to, "Configs"),
                            os.path.join(os.getcwd(), "Configs", config_name))
            shutil.rmtree(os.path.join(extract_to, "Configs"))
            shutil.copytree(os.path.join(extract_to, "Keys"),
                            os.path.join(os.getcwd(), "Keys", config_name))
            shutil.rmtree(os.path.join(extract_to, "Keys"))
            self.myLogger.log("T", "Successfully copied config to target folder.", self.TAG)
        shutil.rmtree(extract_to)
        self.myLogger.log("T", "Successfully removed temp folder.", self.TAG)

    @staticmethod
    def __is_config_available(config_name : str):
        """
        __isConfigAvailable checks name of configs to avoid overriding existing files.

        :param config_name: the name of your config.
        :return: True when config name available, False when config name is taken by another existing config.
        """
        config_name_in_use = []
        for folder_name in os.listdir(os.path.join(os.getcwd(), "Configs")):
            config_name_in_use.append(folder_name)
        return not config_name in config_name_in_use

    def __get_new_config_name(self):
        """
        Private method to get a new config name when rename is required during import.

        Will let user type another name when attempting to use name `currentConfigs` and provide an autogenerated name after 3 unsuccessful attempts.

        :return: Config name string
        """
        print("To avoid overriding existing files, please provide another config name to continue import process.")
        count = 0
        while count < 3:
            new_config_name = input("New config name: ")
            if self.__is_config_available(new_config_name) and len(new_config_name) > 0:
                return new_config_name
            else:
                print("Illegal config name, try another name instead.")
                count += 1
        else:
            new_config_name = "AutoRenamedConfig_" + time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
            print("Using a autogenerated config name to complete import: " + new_config_name)
            return new_config_name

    def export_single_config(self,
                             export_config_folder_name ="current",
                             export_to_dir = None,
                             export_to_file_name = None) -> bool:
        """
        Export a single config as a zip file (with *valid* flag) to the directory you assigned.
        
        In the archive exported you will find a file named `this_is_a_config_file_of_avbpowertool`, which indicates the validity of this file.
        
        When exporting current config, a flag file named `RENAME_REQUIRED` will be added to tell the program that we need a rename before importing it to avoid overriding config.
        (recommended to let users rename it before exporting in order to avoid forgetting the use of this config.)

        :param export_config_folder_name: Determine which config folder you want to export. Set to `current` (case-sensitive) or ignore it will use folder `currentConfigs`.
        :param export_to_dir: Determine where you want to save the exported zip file, keep it empty if you want to save it to the project's **root** folder.
        :param export_to_file_name: Determine the filename of zip file, default value is `myConfig.zip`
        :return: bool
        :raise FileNotFoundError: Config folder assigned not exist.
        """
        if export_to_dir is None:
            export_to_dir = os.getcwd()
        if export_config_folder_name == "current":
            folders_required = (os.path.join(os.getcwd(), "Core", "currentConfigs"),
                               os.path.join(os.getcwd(), "Core", "currentKeySet"))
        else:
            folders_required = (os.path.join(os.getcwd(), "Configs", export_config_folder_name),
                               os.path.join(os.getcwd(), "Keys", export_config_folder_name))
        folder_name_in_archive = ("Configs", "Keys")
        if export_to_file_name is None:
            export_to_file_name = export_config_folder_name + ".zip"
            self.myLogger.log("W", "Use default file name " + export_to_file_name, self.TAG)
        
        if not export_to_file_name.endswith(".zip"):
            self.myLogger.log("W", "Attempting to use other file extension name while exporting config.", self.TAG)
        if not os.path.exists(folders_required[0]):
            self.myLogger.log("W", "Unable to find folder " + folders_required[0], self.TAG)
            raise FileNotFoundError("Assigning a config folder that does not exist.")
        if not os.path.exists(folders_required[1]):
            self.myLogger.log("W", "Unable to find folder " + folders_required[1], self.TAG)
            raise FileNotFoundError("Assigning a config folder that does not exist.")
        

        with zipfile.ZipFile(os.path.join(export_to_dir, export_to_file_name), 'w') as myZip:
            try:
                for i in range(len(folders_required)):
                    for fileName in os.listdir(folders_required[i]):
                        file_path = os.path.join(folders_required[i], fileName)
                        arc_name = os.path.join(folder_name_in_archive[i], fileName)
                        myZip.write(file_path, arc_name)
                        self.myLogger.log("T", "File path: " + file_path, self.TAG)
                        self.myLogger.log("T", "Path in archive: " + arc_name, self.TAG)
            except Exception as e:
                self.myLogger.log("E", "Exception happened when exporting config: " + str(e), self.TAG)
            with open("this_is_a_config_file_of_avbpowertool", "w") as myTempFile:
                myTempFile.write("This is a file that indicates the zip archive is a valid config file of AVBPowerTool.")
            myZip.write("this_is_a_config_file_of_avbpowertool")
            os.remove("this_is_a_config_file_of_avbpowertool")
            if export_config_folder_name == "current":
                with open("RENAME_REQUIRED", "w") as myTempFile:
                    myTempFile.write("Please rename this config before import.")
                myZip.write("RENAME_REQUIRED")
                os.remove("RENAME_REQUIRED")
        return True
    
    @staticmethod
    def get_all_configs(config_dir = None):
        if config_dir is None:
            config_dir = os.path.join(os.getcwd(), "Configs")
        config_list = []
        for i in os.listdir(config_dir):
            config_list.append(i)
        return config_list

if __name__ == "__main__":
    myConfigManager = ConfigManager()
    myConfigManager.import_single_config()