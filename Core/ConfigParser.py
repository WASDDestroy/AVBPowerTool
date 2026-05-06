import json
import os

import Core.EnvironmentChecker as EnvironmentChecker
import Core.LogUtils as LogUtils

DEBUG = True

class ConfigParser:

    def __init__(self) -> None:
        self.TAG = "ConfigParser"
        self.my_logger = LogUtils.LogUtils()
        if os.name == "nt":
            self.my_logger.log("W", "Running on Windows NT, use relative path to avoid chain partition related issues.", self.TAG)
        self.TAG = "ConfigParser"
        self.__IMAGE_DIR = os.path.join(os.getcwd(), "Images")
        self.__KEY_DIR = os.path.join(os.getcwd(), "Core", "currentKeySet") if os.name == "posix" else os.path.join(".\\", "Core", "currentKeySet")
        self.my_logger.log("I", "Instance of ConfigParser successfully created.", self.TAG)

    def cherry_pick_from_config(self, images : list, config_name : str = "current") -> bool:
        """
        Generate a temporary JSON contains info of selected images from original config file.

        :param config_name: the **NAME** of config
        :param images: selected images
        :return: A boolean indicates whether the process succeeded
        """
        try:
            if config_name == "current":
                self.my_logger.log("I", "Create temp file for current config.", self.TAG)
                config_dir = os.path.join(os.getcwd(), "Core", "currentConfigs")
            else:
                self.my_logger.log("W", "Create temporary config for persistent configs is not allowed.", self.TAG)
                return False

            full_config_dic = self.json2_dic(os.path.join(config_dir, "imageInfo.json"))
            self.my_logger.log("I", "Successfully fetched info from current config.", self.TAG)
            temp_config_dic = {}

            for single_image in images:
                temp_config_dic[single_image] = full_config_dic[single_image]
            try:
                json_string = json.dumps(temp_config_dic, indent=4, sort_keys=True)
                with open(os.path.join(os.getcwd(),
                                       "Core",
                                       "currentConfigs",
                                       "tempImageInfo.json"), "w+") as my_file:
                    my_file.write(json_string)
                self.my_logger.log("I", "Temporary image info successfully written into "
                                   + os.path.join(os.getcwd(),
                                                  "Core",
                                                  "currentConfigs",
                                                  "tempImageInfo.json"), "saveResultToFile")
                return True
            except Exception as e:
                self.my_logger.log("I", "Exception happened when saving temp config file. " + str(e), self.TAG)
                return False

        except FileNotFoundError:
            self.my_logger.log("E", "Unable to open config file! Maybe current config is corrupt or active config has no related info!")
            return False

    def remove_cherry_pick_file(self, config_name : str = "current") -> bool:
        try:
            if config_name == "current":
                self.my_logger.log("I", "Create temp file for current config.")
                config_dir = os.path.join(os.getcwd(), "Core", "currentConfigs")
            else:
                self.my_logger.log("W", "Create temporary config for persistent configs is not allowed.", self.TAG)
                return False
            os.remove(os.path.join(config_dir, "tempImageInfo.json"))
            self.my_logger.log("I", "Successfully removed temp cherry-pick file.", self.TAG)
            return True
        except FileNotFoundError as e:
            self.my_logger.log("W", "Unable to access file! " + str(e), self.TAG)
            return False

    def get_image_in_json(self, complete_path_to_json) -> list:
        """
        Read images saved in JSON file.

        :param complete_path_to_json: The directory of config file(json).
        :return: A list contains image names in JSON file
        """

        full_dict = self.json2_dic(complete_path_to_json)
        full_keys = full_dict.keys()
        result_list = []
        for item in full_keys:
            result_list.append(item)
        return result_list

    def get_image_list(self,
                       file_dir = None) -> list[str]:
        """
        getImageList reads config file from assigned directory and returns a list contains image file's **NAME**.

        :param file_dir: The directory of config file.
        :return: A list contains partition file's **NAME**, extension name is excluded.
        :rtype: list[str]
        """
        if file_dir is None:
            file_dir = os.path.join(os.getcwd(),
                                    "Core",
                                    "currentConfigs",
                                    "imageList.txt")
        try:
            if not os.path.exists(file_dir):
                self.my_logger.log("E", "File imageList.txt not found! Check your \"currentConfigs\" dir.")
                return []
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
        if not is_vbmeta:
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

    def json2_dic(self, image_config_file_dir = None) -> dict:
        """
        Parse JSON object to Python dictionary.

        :param image_config_file_dir: The directory of config file, you can freely include filename or not.
        If not, method will use default value imageInfo.json.
        :type image_config_file_dir: str
        :return: Dictionary contains JSON content.
        :rtype: dict
        """
        if image_config_file_dir is None:
            self.my_logger.log("W", "Use default config dir due to empty argument.", self.TAG)
            image_config_file_dir = os.path.join(os.getcwd(), "Core", "currentConfigs", "imageInfo.json")
        if image_config_file_dir.endswith("/") or image_config_file_dir.endswith("\\") or not image_config_file_dir.endswith(".json"):
            self.my_logger.log("W", "Config name not assigned! Use default name.", self.TAG)
            image_config_file_dir = os.path.join(image_config_file_dir, "imageInfo.json")
        self.my_logger.log("D", "Path: " + image_config_file_dir, self.TAG)
        if not os.path.exists(image_config_file_dir):
            self.my_logger.log("E", "Path does not exist!", self.TAG)
            return {}
        with open(image_config_file_dir, "r") as my_file:
            config_dic : dict = json.load(my_file)
        return config_dic

    def get_vbmeta_included_partitions(self, config_name : str = "current", vbmeta_name : str = "vbmeta") -> list:
        """
        Return included images of determined vbmeta image in determined config, such as vbmeta of config "TB710FU_1.5.04.395".
        :param config_name: The name of config. DO NOT post filename. Default to current
        :type config_name: str
        :param vbmeta_name: The name of vbmeta image, such as "vbmeta_system". NO EXTENSION NAME REQUIRED.
        :type vbmeta_name: str
        :return: List of images included.
        :rtype: list
        """
        try:
            if config_name == "current":
                current_dic = self.json2_dic()
            else:
                current_dic = self.json2_dic(
                    os.path.join(os.getcwd(), "Configs", config_name, "imageInfo.json"))
            vbmeta_dic = {}
            for image_name in current_dic:
                if image_name == vbmeta_name:
                    vbmeta_dic = current_dic[image_name]
                    break
            image_required = []

            # In chain partition list, data are stored in a way that makes generate command line for adding chain partition easier,
            # For example, boot partition with chain partition pos 3 will be stored as boot:3:
            # Thus, we only have to assign path to key file to generate corresponding command line, and there we have to handle this special rule.
            for chain_partition in vbmeta_dic["Chain"]:
                image_required.append(chain_partition[:chain_partition.find(":")])

            # For other images included, use normal method .extend() .
            for key in ("Hash", "Hashtree"):
                image_required.extend(vbmeta_dic[key])
            return image_required
        except FileNotFoundError:
            self.my_logger.log("W", "Config file not found.", self.TAG)
            return []

    def generate_vbmeta_seq_list(self, config_name: str = "current", vbmeta_name: str = "vbmeta") -> list:
        """
        Generate a sequential list of vbmeta images.

        This is designed to handle situations such as "vbmeta_system is the chain partition of vbmeta".

        :param config_name: The name of config. DO NOT post filename. Default to current
        :type config_name: str
        :param vbmeta_name: The name of vbmeta image, such as "vbmeta_system". NO EXTENSION NAME REQUIRED.
        :type vbmeta_name: str
        """
        result = [vbmeta_name]
        root_vbmeta_partitions = self.get_vbmeta_included_partitions(config_name, vbmeta_name)
        self.my_logger.log("T", "Image %s contains %s" % (vbmeta_name, str(root_vbmeta_partitions)), self.TAG)
        for partition in root_vbmeta_partitions:
            if "vbmeta" in partition:
                self.my_logger.log("T", "Found vbmeta partition: %s" % partition, self.TAG)
                result.extend(self.generate_vbmeta_seq_list(config_name, partition))
        return result


    def get_all_vbmeta_names(self, config_name : str = "current") -> list:
        """
        Return all vbmeta image names in determined config.
        :param config_name: The name of config. DO NOT post filename. Default to current.
        :return: List of vbmeta image names.
        """
        all_images = self.get_all_image_names(config_name)
        result_list = []
        for image in all_images:
            if "vbmeta" in all_images:
                result_list.append(image)
        return result_list

    def get_all_image_names(self, config_name : str = "current") -> list:
        """
        Return all image names in determined config.
        :param config_name: The name of config. DO NOT post filename. Default to current.
        """
        try:
            if config_name == "current":
                current_dic = self.json2_dic()
            else:
                current_dic = self.json2_dic(
                    os.path.join(os.getcwd(), "Configs", config_name, "imageInfo.json"))
            result_list = []
            for image_name in current_dic.keys():
                result_list.append(image_name)
            return result_list
        except FileNotFoundError:
            self.my_logger.log("W", "Config file not found.", self.TAG)
            return []

class ProgramConfigParser:

    def __init__(self):
        self.my_logger = LogUtils.LogUtils()
