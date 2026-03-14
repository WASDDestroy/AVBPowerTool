import copy
import os
import subprocess

import Core.ConfigParser as ConfigParser
import Core.EnvironmentChecker as EnvironmentChecker
import Core.LogUtils as LogUtils


class SignImages:

    def __init__(self, logger=None) -> None:
        self.TAG = "SignImages"
        if not logger:
            self.my_logger = LogUtils.LogUtils()
            self.my_logger.log(
                "W", "Logger not given, created an instance just now.", self.TAG)
        else:
            self.my_logger = logger
        self.my_config_parser = ConfigParser.ConfigParser(self.my_logger)
        self.__IMAGE_DIR = os.path.join(os.getcwd(), "Images")
        self.my_logger.log(
            "I", "Instance of SignImages successfully created.", self.TAG)

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

    def sign_images_with_output(self, single_config_arg, image_name, success_message_only=False) -> bool:
        """
        Sign single image with console output. Output except success message can be suppressed by parameter success_message_only.

        :param single_config_arg: The list of signing command.
        :param image_name: The name of the image to be signed.
        :param success_message_only: Supress fail messages and 'process ...' message, will be useful when signing vbmeta images.

        :return: A boolean indicates whether the signing process succeeded
        """
        self.my_logger.log("I", "=" * 80, self.TAG)

        if not success_message_only:
            print()
            if "vbmeta" in image_name.lower():
                print("Generating vbmeta image, name: " + image_name)
            else:
                print("Signing image: " + image_name)
        self.my_logger.log("I", "Processing image: " + image_name, self.TAG)

        single_command: list = self.my_config_parser.build_single_avb_tool_command(
            single_config_arg)

        command_for_output: str = ""
        for j in single_command:
            command_for_output += j + " "
        self.my_logger.log("D", "AVBTool command: " + command_for_output, "signImagesBatch")

        avb_tool_result: tuple = self.sign_single_image(single_command)
        self.my_logger.log("D", "stderr from avbtool.py: " +
                           avb_tool_result[1], self.TAG)
        self.my_logger.log("D", "stdout from avbtool.py: " +
                           avb_tool_result[2], self.TAG)
        if avb_tool_result[0]:
            if "vbmeta" in image_name.lower():
                print("Successfully generated vbmeta image: " + image_name)
            else:
                print("Successfully signed " + image_name)
            self.my_logger.log(
                "D", "Successfully processed image: " + image_name, self.TAG)
            return True
        else:
            if not success_message_only:
                if "vbmeta" in image_name.lower():
                    print("Failed to generate vbmeta image: " + image_name)
                    print(
                        "Check your images manually, make sure that all images are signed properly.")
                else:
                    print("Failed to sign " + image_name)
            self.my_logger.log(
                "W", "Failed to process image: " + image_name, self.TAG)
            return False

    def sign_images_batch(self,
                          image_config_file_dir=None,
                          remove_footers_first=False,
                          remove_vb=True):
        """
        Sign images in <ProjectDir>/Images dir with embedded avbtool.

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
                        self.my_logger.log(
                            "I", "Removed vbmeta image: " + i, self.TAG)
                    except Exception as e:
                        self.my_logger.log(
                            "W", "Exception happened when removing vbmeta images: " + repr(e), self.TAG)
                        return False, ["FAILED_TO_REMOVE_VB"]
        config_dic = self.my_config_parser.json2_dic(image_config_file_dir)
        # self.my_logger.log("D", str(config_dic), self.TAG)
        vbmeta_list = []
        self.my_logger.log("I", "First, sign non-vbmeta images.", self.TAG)
        for i in config_dic:
            if "vbmeta" in i.lower():
                vbmeta_list.append(i)
                continue
            sign_result = self.sign_images_with_output(config_dic[i], i)
            if not sign_result:
                return False, ["FAILED_TO_SIGN_" + i]

        self.my_logger.log("I", "Then generate vbmeta images.", self.TAG)

        total_times = 0
        fail_list = copy.deepcopy(vbmeta_list)
        while total_times < 10 and fail_list:
            fail_list = []
            for i in range(len(vbmeta_list)):
                vbmeta_result = self.sign_images_with_output(config_dic[vbmeta_list[i]], vbmeta_list[i],success_message_only=True)
                if not vbmeta_result:
                    fail_list.append(vbmeta_list[i])
                    self.my_logger.log("W", "Failed to generate vbmeta image: " + vbmeta_list[i], self.TAG)
                    self.my_logger.log("D", "Current fail list: " + str(fail_list), self.TAG)
            vbmeta_list = copy.deepcopy(fail_list)
            total_times += 1
        if total_times >= 10:
            self.my_logger.log("W", "Failed to generate vbmeta image!", self.TAG)
            self.my_logger.log("W", "These vbmeta images have not been generated: " + str(fail_list), self.TAG)
            return False, ["FAILED_TO_GENERATE_VB_" + str(fail_list)]
        self.my_logger.log("I", "Successfully signed all images.", self.TAG)
        return True, []

    def remove_all_footers(self):
        """
        Remove all footers of images in <root_dir>/Images before signing process.
        """
        command_list = [EnvironmentChecker.EnvironmentChecker.detect_python_command(),
                        os.path.join(os.getcwd(), "Core", "avbtool.py"),
                        "erase_footer",
                        "--image",
                        "<image_file>"]
        image_list = self.my_config_parser.get_image_list()
        for i in image_list:
            command_list[-1] = os.path.join(self.__IMAGE_DIR, i + ".img")
            result = subprocess.run(
                command_list, capture_output=True, text=True)
            self.my_logger.log("I", "avbtool.py returns with code: " + str(
                result.returncode) + "when processing image" + command_list[-1], "removeAllFooters")


if __name__ == "__main__":
    my_image_signer = SignImages()
    my_image_signer.sign_images_batch()
