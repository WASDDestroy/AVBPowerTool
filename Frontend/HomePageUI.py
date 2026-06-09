import Frontend.BaseUI as BaseUI
import Frontend.DisplayAVBInfo as DisplayAVBInfo
from Core.Localization import t

class HomePageUI(BaseUI.BaseUI):

    def customized_init(self):
        self.TAG = "HomePageUI"
        self.customized_function = {
            "V": {"id": "action:view_current_config_info", "label": t("home.action.view_current_config_info")}
        }
        # noinspection PyAttributeOutsideInit

    def call_backend(self, function_name: str):
        if function_name == self.customized_function["V"]["id"]:
            DisplayAVBInfo.entry()  # type: ignore


if __name__ == "__main__":
    myHomePage = HomePageUI()
    while 1:
        myHomePage.entry()
