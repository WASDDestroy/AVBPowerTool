import os
import subprocess

import DynamicImportUtils
import LogUtils


class SignImages:

    def __init__(self, logger=None) -> None:
        if not logger:
            self.myLogger = LogUtils.LogUtils()
            self.myLogger.log(
                "W", "Logger not given, created an instance just now.", "SignImages")
        else:
            self.myLogger = logger
        self.myImporter = DynamicImportUtils.DynamicImportUtils(
            logger=self.myLogger)
        self.myConfigParser = self.myImporter.create_instance(self.myImporter.import_module("ConfigParser"),
                                                             "ConfigParser",
                                                              self.myLogger)
        self.TAG = "ImageSigner"
        self.__IMAGE_DIR = os.path.join(os.getcwd(), "Images")
        self.myLogger.log(
            "I", "Instance of SignImages successfully created.", "SignImages")

    @staticmethod
    def sign_single_image(signing_command: list) -> tuple:
        """
        Receive a command list and run it via subcommand.

        :param signing_command: The list of signing command.
        :return: A tuple contains three items:
        1. bool, indicates whether the signing process successes
        2. string, standard error of avbtool.py
        3. string, standard output of avbtool.py

        :rtype: tuple(bool, str, str)
        """
        result = subprocess.run(signing_command, capture_output=True, text=True)
        sign_result = (result.returncode == 0,
                      result.stderr if result.stderr else "Empty",
                      result.stdout if result.stdout else "Empty")
        return sign_result

    def sign_images_with_output(self, single_config_arg, image_name):
        """
        Logic extracted from signImagesBatch
        """
        self.myLogger.log("I", "=" * 80, self.TAG)
        if "vbmeta" in image_name.lower():
            print("Generating vbmeta image, name: " + image_name)
        else:
            print("Signing image: " + image_name)
        self.myLogger.log("I", "Processing image: " + image_name, self.TAG)
        single_command: list = self.myConfigParser.build_single_avb_tool_command(
            single_config_arg)
        self.myLogger.log(
            "D", "================================AVB COMMAND================================", "signImagesBatch")
        command_for_output: str = ""
        for j in single_command:
            command_for_output += j + " "
        self.myLogger.log("D", command_for_output, "signImagesBatch")
        self.myLogger.log(
            "D", "===========================================================================", "signImagesBatch")
        avb_tool_result: tuple = self.sign_single_image(single_command)
        if avb_tool_result[0]:
            if "vbmeta" in image_name.lower():
                print("Successfully generated vbmeta image: " + image_name)
            else:
                print("Successfully signed " + image_name)
            self.myLogger.log(
                "D", "Successfully processed image: " + image_name)
        else:
            if "vbmeta" in image_name.lower():
                print("Failed to generate vbmeta image: " + image_name)
                print(
                    "Check your images manually, make sure that all images are signed properly.")
            else:
                print("Failed to sign " + image_name)
            self.myLogger.log(
                "W", "Failed to process image: " + image_name, self.TAG)
        self.myLogger.log("D", "stderr from avbtool.py: " +
                          avb_tool_result[1], self.TAG)
        self.myLogger.log("D", "stdout from avbtool.py: " +
                          avb_tool_result[2], self.TAG)
        print()

    def sign_images_batch(self,
                          image_config_file_dir=None,
                          remove_footers_first=False,
                          remove_vb=True):
        """
        Sign images in <ProjectDir>/images dir.

        :param image_config_file_dir: The directory of config file. Config file name is optional.
        :param remove_footers_first: Choose whether the program removes footers before signing process.
        :param remove_vb: Whether the program removes vbmeta images before signing. (Will generate new vbmeta images.)
        """
        if image_config_file_dir is None:
            image_config_file_dir = os.path.join(os.getcwd(),
                                              "Core",
                                              "currentConfigs",
                                              "imageInfo.json")
        if not image_config_file_dir.endswith(".json"):
            image_config_file_dir += "imageInfo.json"
        if remove_footers_first:
            self.remove_all_footers()
        if remove_vb:
            for i in os.listdir(self.__IMAGE_DIR):
                if "vbmeta" in i.lower():
                    try:
                        os.remove(os.path.join(self.__IMAGE_DIR, i))
                        self.myLogger.log(
                            "I", "Removed vbmeta image: " + i, self.TAG)
                    except Exception as e:
                        self.myLogger.log(
                            "W", "Exception happened when removing vbmeta images: " + repr(e), self.TAG)
        config_dic = self.myConfigParser.json2_dic(image_config_file_dir)
        self.myLogger.log("D", str(config_dic), self.TAG)
        vbmeta_list = []
        self.myLogger.log("I", "First, sign non-vbmeta images.")
        for i in config_dic:
            if "vbmeta" in i.lower():
                vbmeta_list.append(i)
                continue
            self.sign_images_with_output(config_dic[i], i)

        self.myLogger.log("I", "Then generate vbmeta images.")
        for i in vbmeta_list:
            self.sign_images_with_output(config_dic[i], i)

    def remove_all_footers(self):
        command_list = ["python3",
                        os.path.join(os.getcwd(), "Core", "avbtool.py"),
                        "erase_footer",
                        "--image",
                        "<image_file>"]
        if os.name == "nt":
            command_list[0] = "py"
        image_list = self.myConfigParser.get_image_list()
        for i in image_list:
            command_list[-1] = os.path.join(self.__IMAGE_DIR, i + ".img")
            result = subprocess.run(
                command_list, capture_output=True, text=True)
            self.myLogger.log("I", "avbtool.py returns with return code: " + str(
                result.returncode) + "when processing image" + command_list[-1], "removeAllFooters")


if __name__ == "__main__":
    myImageSigner = SignImages()
    myImageSigner.sign_images_batch()
