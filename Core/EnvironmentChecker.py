import os
import subprocess

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