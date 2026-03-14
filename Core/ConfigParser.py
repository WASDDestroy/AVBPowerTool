import json
import os

import Core.EnvironmentChecker as EnvironmentChecker
import Core.LogUtils as LogUtils

DEBUG = True

class ConfigParser:

    def __init__(self, logger = None) -> None:
        self.TAG = "ConfigParser"
        if not logger:
            self.my_logger = LogUtils.LogUtils()
            self.my_logger.log("W", "Logger not given, created an instance just now.", self.TAG)
        else:
            self.my_logger = logger
        self.my_logger.log("I", "Instance of ConfigParser successfully created.", self.TAG)
        if os.name == "nt":
            self.my_logger.log("W", "Running on Windows NT, use relative path to avoid chain partition related issues.")
        self.TAG = "ConfigParser"
        self.__IMAGE_DIR = os.path.join(os.getcwd(), "Images")
        self.__KEY_DIR = os.path.join(os.getcwd(), "Core", "currentKeySet") if os.name == "posix" else os.path.join(".\\", "Core", "currentKeySet")

    def get_image_list(self,
                       file_dir = None) -> list[str]:
        """
        getImageList reads config file from assigned directory and returns a list contains image file's **NAME**.

        :param file_dir: The directory of config file.
        :return: A list contains partition file's **NAME**.
        :rtype: list[str]
        """
        if file_dir is None:
            file_dir = os.path.join(os.getcwd(),
                                    "Core",
                                    "currentConfigs",
                                    "imageList.txt")
        try:
            with open(file_dir, "r") as my_file:
                self.my_logger.log("I", "Successfully opened config file.", self.TAG)
                skip_list = ["#", " ", "\n"]
                image_list = []
                file_lines = my_file.readlines()
                for file_reader in file_lines:
                    if file_reader[0] in skip_list or len(file_reader) == 0:
                        self.my_logger.log("I", "Skipping line: " + file_reader.strip("\n"), self.TAG)
                    else:
                        file_reader = file_reader.strip("\n")
                        self.my_logger.log("I", "Image name to be appended: " + file_reader + ".img", self.TAG)
                        image_list.append(file_reader)
        except FileNotFoundError:
            self.my_logger.log("E", "File not found! Check your \"currentConfigs\" dir.")
            raise FileNotFoundError
        return image_list
    
    def build_single_avb_tool_command(self, single_config_dict : dict):
        """
        Generate AVBTool command for a single image from dictionary given.
        
        :param single_config_dict: Config directory. Contains image name, rollback index, etc.
        :return: A dictionary contains command args accepted by subprocess.run()
        :rtype: list
        :see: Core/ImageInfoUtils.py
        """
        is_vbmeta = False
        if "vbmeta" in single_config_dict["Image File"].lower():
            is_vbmeta = True
        # Determine python and script file
        command_header = EnvironmentChecker.EnvironmentChecker.detect_python_command()
        if command_header is None:
            raise RuntimeError("Unable to find proper Python")
        command_list = [command_header, os.path.join(os.getcwd(), "Core", "avbtool.py")]
        # Detect image type and take proper action
        if is_vbmeta:
            self.my_logger.log("I", "Generating VBMeta generation command for " + single_config_dict["Image File"] + ".", self.TAG)
            command_list.append("make_vbmeta_image")
            command_list.extend(["--output", os.path.join(self.__IMAGE_DIR, single_config_dict["Image File"])])
            # Add command for chain partition
            if len(single_config_dict["Chain"]) != 0: # If there is/are chain partition(s) need to be added
                for i in range(len(single_config_dict["Chain"])):
                    command_list.extend(["--chain_partition",
                                        single_config_dict["Chain"][i]
                                        + os.path.join(self.__KEY_DIR, single_config_dict["Chain partition key"][i])])
            # Add command for other partitions to be included
            for i in ["Hash", "Hashtree"]:
                if len(single_config_dict[i]) != 0: # If this type of partition do exist
                    for j in single_config_dict[i]:
                        if not os.path.exists(os.path.join(self.__IMAGE_DIR, j + ".img")):
                            raise RuntimeError("Required image %s not found!"%(os.path.join(self.__IMAGE_DIR, j + ".img")))
                        command_list.extend(["--include_descriptors_from_image",
                                            os.path.join(self.__IMAGE_DIR, j + ".img")])
        else:
            self.my_logger.log("I", "Generating normal image signing command for " + single_config_dict["Image File"] + ".", self.TAG)
            if single_config_dict["Descriptor Type"] == "Hash":
                self.my_logger.log("I", "Adding hash footer command.", self.TAG)
                command_list.append("add_hash_footer")
                command_list.extend(["--partition_size", single_config_dict["Image size"]])
            else:
                self.my_logger.log("I", "Adding hashtree footer command.", self.TAG)
                command_list.append("add_hashtree_footer")
                if os.name == "nt":
                    command_list.append("--do_not_generate_fec")
                    self.my_logger.log("W", "Running on Windows, skipping FEC encoding.", self.TAG)
            # Add common args for non-vbmeta images
            if not os.path.exists(os.path.join(self.__IMAGE_DIR, single_config_dict["Image File"])):
                raise RuntimeError("Required image %s not found!" % (os.path.join(self.__IMAGE_DIR, single_config_dict["Image File"])))
            command_list.extend(["--image", os.path.join(self.__IMAGE_DIR, single_config_dict["Image File"]),
                "--partition_name", single_config_dict["Partition Name"],
                "--salt", single_config_dict["Salt"]])
        # Add shared configs
        if single_config_dict["Algorithm"] != "NONE":
            command_list.extend(["--algorithm", single_config_dict["Algorithm"],
                                "--key", os.path.join(self.__KEY_DIR, single_config_dict["Public key file"])])
        else:
            command_list.extend(["--hash_algorithm", single_config_dict["Hash Algorithm"]])
        command_list.extend(["--rollback_index", single_config_dict["Rollback Index"]])
        for i in single_config_dict["Props"]:
            command_list.extend(["--prop", i + ":" + single_config_dict["Props"][i]])
        self.my_logger.log("I", "Success.", self.TAG)
        return command_list
    
    def get_config_name(self,
                        config_dir = None) -> str:
        """
        Get the name of a config by parsing config.cfg.

        Return the name of current config if arg `configDir` is not given.

        Will return nothing when config file cannot be reached.

        :param config_dir: The directory of config.cfg. DO NOT post filename.
        :type config_dir: str
        :return: The name of config.
        :rtype: str
        """
        if config_dir is None:
            config_dir = os.path.join(os.getcwd(), "Core", "currentConfigs")
        try:
            with open(os.path.join(config_dir, "config.cfg"), "r") as myFile:
                file_lines = myFile.readlines()
                self.my_logger.log("D", str(file_lines), self.TAG)
                for i in file_lines:
                    split_line = i.split(":")
                    if split_line[0] == "Config Name":
                        return split_line[1].lstrip(" ").rstrip("\n")
                else:
                    self.my_logger.log("W", "Found config file, but file doesn't contain valid info.", self.TAG)
                    return ""
        except FileNotFoundError:
            self.my_logger.log("W", "Config file not found!", self.TAG)
            return ""
    
    @staticmethod
    def json2_dic(image_config_file_dir = None) -> dict:
        """
        Parse JSON object to Python dictionary.

        :param image_config_file_dir: The directory of config file, you can freely include filename or not.
        If not, method will use default value imageInfo.json.
        :type image_config_file_dir: str
        :return: Dictionary contains JSON content.
        :rtype: dict
        """
        if image_config_file_dir is None:
            image_config_file_dir = os.path.join(os.getcwd(), "Core", "currentConfigs", "imageInfo.json")
        if image_config_file_dir.endswith("/") or image_config_file_dir.endswith("\\"):
            image_config_file_dir += "imageInfo.json"
        with open(image_config_file_dir, "r") as myFile:
            config_dic : dict = json.load(myFile)
        return config_dic