import BaseUI


class ReadImageInfoUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "ReadImageInfoUI"
        self.customized_function = {
            "A": "Read info of all images",
            "S": "Read info of selected image(s) (NOT RECOMMENDED)",
        }
        # noinspection PyAttributeOutsideInit
        self.mImageInfoUtils = self.my_importer.create_instance(self.my_importer.import_module("ImageInfoUtils"),
                                                              "ImageInfoUtils",
                                                                self.my_logger)
        # noinspection PyAttributeOutsideInit
        self.mConfigParser = self.my_importer.create_instance(self.my_importer.import_module("ConfigParser"),
                                                            "ConfigParser",
                                                              self.my_logger)

    def call_backend(self, function_name: str):
        if function_name == "Read info of all images":
            self.__handle_read_all_images_info()
        # elif functionName == "Read info of selected image(s) (NOT RECOMMENDED)":

    def __handle_read_selected_images_info(self):
        pass

    def __handle_read_all_images_info(self):
        if self.confirm_operation():
            check_result = self.mImageInfoUtils.check_image_exists(
                image_info_list=self.mConfigParser.get_image_list())
            if not check_result[0]:
                print("WARNING: Image mismatch!")
                if check_result[1] == "MORE":
                    print("These images are unnecessary, consider remove them:")
                    for i in check_result[2]:
                        print(i)
                elif check_result[1] == "LESS":
                    print(
                        "These images are missing, you must have them to continue process:")
                    for i in check_result[2]:
                        print(i)
                elif check_result[1] == "DIFF":
                    print("Necessary image(s) not found!")
                    print("Config list:")
                    for i in self.mConfigParser.get_image_list():
                        print(i)
                    print("You have these images:")
                    for i in check_result[3]:
                        print(i)
                self.my_ui_utils.press_enter_to_continue()
                return
            else:
                try:
                    self.mImageInfoUtils.read_image_info_batch(
                        self.mConfigParser.get_image_list())
                    print("Successfully read info of all images.")
                except:
                    print("Operation failed.")
        else:
            print("Operation cancelled.")
        self.my_ui_utils.press_enter_to_continue()
