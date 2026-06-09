import os
import subprocess
import sys
import threading
from typing import List, Optional, Set

import Core.EnvironmentChecker as EnvironmentChecker
import Core.GlobalConfigUtils as GlobalConfigUtils
import Core.LogUtils as LogUtils
from Core.Localization import t


class UIUtils:

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if UIUtils._initialized:
            return
        with UIUtils._lock:
            if UIUtils._initialized:
                return
        self.TAG = "UIUtils"
        self.my_logger = LogUtils.LogUtils()
        self.my_logger.log("I", "Successfully created UIUtils instance.", self.TAG)
        __global_config = GlobalConfigUtils.GlobalConfigInfo()
        self.__should_clear_screen = int(__global_config.get_value("allow_clear_screen"))
        UIUtils._initialized = True

    def clear_screen(self):
        if not self.__should_clear_screen:
            return
        try:
            result = subprocess.run(["cls"], shell=True) if os.name == "nt" else subprocess.run(["clear"], shell=True)
            if result.returncode != 0 or EnvironmentChecker.EnvironmentChecker.is_in_ide():
                self.my_logger.log(
                    "W",
                    "Unable to run command %s on platform %s, try alternate method to clear screen."
                    % ("cls" if os.name == "nt" else "clear", os.name),
                    self.TAG)
                supports_ansi = sys.stdout.isatty() and not (os.name == 'nt' and not os.getenv('ANSICON'))
                self.my_logger.log("D", "ANSI sequence support: %d" % supports_ansi, self.TAG)
                if supports_ansi:
                    sys.stdout.write("\033[2J\033[H")
                    sys.stdout.flush()
                else:
                    print("\n" * 100)
        except FileNotFoundError:
            self.my_logger.log(
                "W",
                "Unable to run clear screen command on platform %s due to FileNotFoundError" % os.name,
                self.TAG)

    @staticmethod
    def press_enter_to_continue(prompt=""):
        input(prompt or t("ui.press_enter"))

    @staticmethod
    def confirm_operation(prompt=None, selection=None) -> bool:
        prompt = prompt or t("ui.confirm_operation")
        selection = selection or (t("ui.yes"), t("ui.no"))
        my_selector = EnhancedFileSelectorUI(prompt, selection, False, True, True)
        return my_selector.show(show_instructions=False)[0] == selection[0]

    @staticmethod
    def message_on_fail(prompt=""):
        if prompt:
            print(prompt)
        else:
            print(t("ui.operation_failed"))
            print(t("ui.refer_to_log"))
            print(t("ui.check_log_note"))

    @staticmethod
    def message_on_cancel(prompt=""):
        print(prompt or t("ui.operation_canceled"))


class EnhancedFileSelectorUI:
    """
    An enhanced "file" selector.

    Supports keyboard navigation, multi-select and infinite roll.
    """

    def __init__(self, title: str = None, items: List[str] = None, multi_select: bool = False,
                 infinite_roll=True, cancelable=True):  # type: ignore
        self.title = title or t("ui.select_files")
        self.items = items or []
        self.multi_select = multi_select
        self.selected_indices: Set[int] = set()
        self.current_index = 0
        self.finished = False
        self.cancelled = False
        self.infinite_roll = infinite_roll
        self.cancelable = cancelable
        self.TAG = "EnhancedFileSelectorUI"
        self.my_logger = LogUtils.LogUtils()
        self.my_ui_utils = UIUtils()

    def show(self, show_instructions=True, allow_long_item=False) -> Optional[List[str]]:
        if not self.items:
            print(t("ui.no_items_to_select"))
            return None if not self.multi_select else []

        self.selected_indices.clear()
        self.current_index = 0
        self.finished = False
        self.cancelled = False

        while not self.finished:
            self._draw_ui(show_instructions, allow_long_item)
            self._process_input()

        if self.cancelled:
            return []

        selected_items = [self.items[i] for i in sorted(self.selected_indices)]

        if not self.multi_select and selected_items:
            return [selected_items[0]]

        return selected_items

    def _draw_ui(self, show_instructions=True, allow_long_item=False) -> None:
        self.my_ui_utils.clear_screen()

        print("=" * 80)
        title_line = f"  {self.title:^80}  "
        print(title_line)
        print("=" * 80)

        if show_instructions:
            print("  " + t("ui.instructions"))
            print("    " + t("ui.navigate_items"))
            if self.multi_select:
                print("    " + t("ui.space_select"))
                print("    " + t("ui.select_all"))
            print("    " + t("ui.enter_confirm"))
            if self.cancelable:
                print("    " + t("ui.esc_cancel"))
            print("=" * 80)

        if not self.items:
            print("  " + t("ui.no_items_available").ljust(45))
        else:
            for i, item in enumerate(self.items):
                display_item = item
                if len(display_item) > 35 and not allow_long_item:
                    display_item = display_item[:32] + "..."

                if i == self.current_index:
                    prefix = "→ "
                else:
                    prefix = "  "

                if self.multi_select:
                    checkbox = "[✓]" if i in self.selected_indices else "[ ]"
                else:
                    checkbox = "[●]" if i in self.selected_indices else "[○]"

                line = f"{prefix}{checkbox} {display_item}"
                line = line.ljust(80)
                print(f"  {line}  ")

        print("=" * 80)

        if self.multi_select:
            selected_count = len(self.selected_indices)
            status = t("ui.selected_count", selected=selected_count, total=len(self.items))
            print(f"  {status:^80}  ")
            print("=" * 80)

        if self.cancelable:
            print("  " + t("ui.buttons_confirm_cancel"))
        else:
            print("  " + t("ui.buttons_confirm"))
        print("=" * 80)

    def _process_input(self) -> None:
        try:
            if os.name == 'nt':
                import msvcrt
                key = msvcrt.getch().decode('utf-8', errors='ignore')
            else:
                import select
                import termios
                import tty
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    raw = os.read(fd, 1)

                    if raw == b'\x1b':
                        r, _, _ = select.select([fd], [], [], 0.05)
                        if r:
                            raw += os.read(fd, 4)

                    key = raw.decode('utf-8', errors='ignore')

                    if len(raw) == 3 and raw[:2] == b'\x1b[':
                        if raw == b'\x1b[A':
                            key = '\x48'
                        elif raw == b'\x1b[B':
                            key = '\x50'
                        elif raw == b'\x1b[D':
                            key = '\x48'
                        elif raw == b'\x1b[C':
                            key = '\x50'
                    elif len(raw) == 3 and raw[:2] == b'\x1bO':
                        if raw == b'\x1bOA':
                            key = '\x48'
                        elif raw == b'\x1bOB':
                            key = '\x50'
                        elif raw == b'\x1bOD':
                            key = '\x48'
                        elif raw == b'\x1bOC':
                            key = '\x50'
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except (ImportError, Exception) as e:
            self.my_logger.log(
                "W",
                f"termios/raw input failed ({e}), falling back to input()",
                self.TAG)
            key = input("").lower()
            if len(key) > 0:
                key = key[0]
            else:
                key = ''

        if key == '\x1b' and self.cancelable:
            self.cancelled = True
            self.finished = True
            return

        elif key == '\r' or key == '\n':
            if not self.multi_select and not self.selected_indices:
                self.selected_indices.add(self.current_index)
            self.finished = True
            return

        elif key in ['w', 'W', '\x48']:
            if self.current_index > 0:
                self.current_index -= 1
            elif self.infinite_roll:
                self.current_index = len(self.items) - 1

        elif key in ['s', 'S', '\x50']:
            if self.current_index < len(self.items) - 1:
                self.current_index += 1
            elif self.infinite_roll:
                self.current_index = 0

        elif key == ' ':
            if self.multi_select:
                if self.current_index in self.selected_indices:
                    self.selected_indices.remove(self.current_index)
                else:
                    self.selected_indices.add(self.current_index)
            else:
                self.selected_indices.clear()
                self.selected_indices.add(self.current_index)

        elif key in ['a', 'A'] and self.multi_select:
            if len(self.selected_indices) == len(self.items):
                self.selected_indices.clear()
            else:
                self.selected_indices = set(range(len(self.items)))

    @staticmethod
    def _get_key() -> str:
        try:
            import msvcrt
            return msvcrt.getch().decode('utf-8', errors='ignore')
        except (ImportError, Exception):
            user_input = input("")
            return user_input[0] if user_input else ''
