import os
import subprocess
import threading

class EnvironmentChecker:
    @staticmethod
    def detect_python_command():
        """
        Detect available command for starting Python 3 on current system.
        
        Note:
            - Detects Python 3 only.
            - Return first available command when multiple command are available.

        :return: Available Python command, such as python3, python and py.
        :rtype: str
        """

        if os.name == 'nt':
            commands_to_try = [
                'py',        # Python launcher for Windows
                'python',    # Newer Python version, for instance, Python 3.13
                'python3',   # Backup
            ]
        else: # Posix
            commands_to_try = [
                'python3',   # Typical situation
                'python',    # Backup
            ]

        for cmd in commands_to_try:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False
                )

                if result.returncode == 0:
                    version_output = (result.stdout + result.stderr).lower()

                    if 'python' in version_output and 'python 2' not in version_output:
                        return cmd
                        
            except (subprocess.SubprocessError, FileNotFoundError, PermissionError, OSError):
                continue

        # Return None if no command available
        return None
    
    @staticmethod
    def check_necessary_folders(logger):
        """
        Check necessary folders when program starts up.

        Necessary folders:

        - <root_dir>/Images
        - <root_dir>/Configs
        - <root_dir>/Core/currentConfigs
        - <root_dir>/Core/currentKeySet

        :param logger: logger instance.
        """
        tag = "FolderChecker"
        folder_tuple = ("Images",
                       "Configs",
                        "Keys",
                       os.path.join("Core", "currentConfigs"),
                       os.path.join("Core", "currentKeySet"))
        work_dir = os.getcwd()
        for i in folder_tuple:
            current_dir = os.path.join(work_dir, i)
            if not os.path.exists(current_dir):
                os.mkdir(current_dir)
                logger.log("I", "Folder %s does not exist, automatically created it." % i, tag)
            else:
                logger.log("I", "Folder %s exists." % i, tag)

    @staticmethod
    def is_wsl():
        wsl_env_vars = [
            'WSLENV',
            'WSL_DISTRO_NAME',
            'WSL_INTEROP',
            'WSL_UTF8'
        ]

        env_results = {}
        for var in wsl_env_vars:
            env_results[var] = os.environ.get(var, 'Not set')

        is_wsl = any(os.environ.get(var) for var in wsl_env_vars)
        return env_results, is_wsl

    @staticmethod
    def check_fec_state():
        # if os.name == "nt":
        #     return False
        # else:
        #     subprocess.run(["command", "-v", "fec"])
        pass
    
    @staticmethod
    def check_libs():
        """
        Check whether necessary libraries are installed.

        Will return True, [] when all requirements are satisfied, else, False with a list of missing libraries will be returned.
        """
        import importlib.util
        lack_libs = []
        # TODO: Use lib names from requirements.txt instead of hardcoded library import string
        for library_name in ("reedsolo", "numpy"):
            if importlib.util.find_spec(library_name) is None:
                lack_libs.append(library_name)
        if lack_libs:
            return False, lack_libs
        else:
            return True, []
                 


class EnvironmentInfo:

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EnvironmentInfo._initialized:
            return
        with EnvironmentInfo._lock:
            if EnvironmentInfo._initialized:
                return
        self.python_command = None
        EnvironmentInfo._initialized = True
        pass

    def get_python_command(self):
        if self.python_command is None:
            self.python_command = EnvironmentChecker.detect_python_command()
        return self.python_command