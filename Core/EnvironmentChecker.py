import os
import subprocess

class EnvironmentChecker:
    @staticmethod
    def detect_python_command():
        """
        检测系统上可用的Python 3启动命令
        
        返回:
            str: 可用的Python命令（如 'python3', 'python', 'py' 等）
        
        注意:
            - 只检测Python 3相关的命令
            - 当匹配到多个可用命令时，返回第一个找到的
            - 仅支持Windows和Linux平台
        """
        # 根据操作系统确定要尝试的命令列表
        if os.name == 'nt':  # Windows
            commands_to_try = [
                'py',        # Python launcher for Windows
                'python',    # 可能指向Python 3
                'python3',   # 如果安装了Python 3
            ]
        else:  # Linux/Unix (os.name == 'posix')
            commands_to_try = [
                'python3',   # 首选Python 3
                'python',    # 回退到默认Python（在某些系统上可能是Python 3）
            ]
        
        # 尝试每个命令
        for cmd in commands_to_try:
            try:
                # 执行版本查询，只检查命令是否存在且可执行
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False
                )
                
                # 检查命令是否成功执行且输出包含Python 3相关信息
                if result.returncode == 0:
                    version_output = (result.stdout + result.stderr).lower()
                    
                    # 确保是Python且不是Python 2
                    if 'python' in version_output and 'python 2' not in version_output:
                        return cmd
                        
            except (subprocess.SubprocessError, FileNotFoundError, PermissionError, OSError):
                # 命令执行失败，继续尝试下一个
                continue
        
        # 如果没有找到任何可用的命令，返回None
        return None
    
    @staticmethod
    def check_necessary_folders(logger):
        tag = "FolderChecker"
        folder_tuple = ("Images",
                       "Configs",
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