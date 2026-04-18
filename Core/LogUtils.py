"""
LogUtils provides log ability for programs. Destination can be manually assigned in __init__().

log(): Log a string to destination you assigned when an instance is created.

setLogLevel(): Set when should LogUtils *starts* to log it to destination.

:author: WASD_Destroy
"""
import os
import time
import threading


class LogUtils:

    __log_level = "T"
    __LOG_LEVEL_DIC = {"A" : 0,
                       "T" : 1,
                       "D" : 2,
                       "I" : 3,
                       "W" : 4,
                       "E" : 5,
                       "F" : 6,
                       "O" : 7}

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # Determine log destination, console is the default option.
    def __init__(self,
                 output = "file",
                 should_attach_time = False,
                 log_dir = None,
                 instant_mode = False) -> None:
        if LogUtils._initialized:
            return
        with LogUtils._lock:
            if LogUtils._initialized:
                return
        self.instantMode = instant_mode
        self.isLogToFile = True
        self.__shouldAttachTime = should_attach_time
        if log_dir is None:
            log_dir = os.path.join(os.getcwd(), "Logs")
        if output.lower() != "console":
            try:
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                file_name = os.path.join(log_dir,
                                        "log_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".log")
                self.logFile = open(file_name, "w+", encoding = "UTF-8")
                self.isLogToFile = True
                print(f"Log file created at: {file_name}")
            except PermissionError:
                print(f"Warning: Cannot create log directory at {log_dir}, falling back to console output")
                self.isLogToFile = False
            except Exception as e:
                print(f"Warning: Error creating log file: {e}, falling back to console output")
                self.isLogToFile = False
        self.log("I", "Logger instance created.", "LogUtils")
        LogUtils._initialized = True
    def __del__(self) -> None:
        if hasattr(self, 'logFile') and self.logFile:
            # noinspection PyBroadException
            try:
                self.logFile.close()
            except:
                pass

    # Construct log strings
    def __construct_trace(self, verbose_str):
        tmp_str = ""
        if self.__shouldAttachTime:
            tmp_str = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[TRACE] " + tmp_str + verbose_str

    def __construct_debug(self, debug_str):
        tmp_str = ""
        if self.__shouldAttachTime:
            tmp_str = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[DEBUG] " + tmp_str + debug_str

    def __construct_info(self, info_str):
        tmp_str = ""
        if self.__shouldAttachTime:
            tmp_str = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[INFO] " + tmp_str + info_str
    
    def __construct_warn(self, warn_str):
        tmp_str = ""
        if self.__shouldAttachTime:
            tmp_str = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[WARN] " + tmp_str + warn_str
    
    def __construct_error(self, error_str):
        tmp_str = ""
        if self.__shouldAttachTime:
            tmp_str = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[ERROR] " + tmp_str + error_str
    
    def __construct_fatal(self, error_str):
        tmp_str = ""
        if self.__shouldAttachTime:
            tmp_str = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[FATAL] " + tmp_str + error_str
    
    def __process_log_string(self, log_level : str, log_str : str) -> str:
        log_level = log_level.upper()[0]
        if log_level == "T" or log_level == "V": # Back-compatible
            log_info = self.__construct_trace(log_str)
        elif log_level == "D":
            log_info = self.__construct_debug(log_str)
        elif log_level == "I":
            log_info = self.__construct_info(log_str)
        elif log_level == "W":
            log_info = self.__construct_warn(log_str)
        elif log_level == "E":
            log_info = self.__construct_error(log_str)
        elif log_level == "F":
            log_info = self.__construct_fatal(log_str)
        else:
            log_info = self.__construct_warn(log_str) \
                + " (Log level not specified or typo mistake)"
        return log_info
    
    def log(self, log_level : str, log_str : str, log_object ="[Logger]"):
        """
        log() provides constant log realization for all scripts.

        Format: `[Log Level] [Log Object] [Time] <Log Content>`

        Empty <Log Content> string or "\\n" will be ignored.

        :param log_level: Determine your log's level, V,D,I,W,E(non-case-sensitive)
        or any string start with these 5 letters are accepted. Default value is W.
        :type log_level: str
        :param log_str: Log content. Will get empty output if type `\\n` or keep it empty
        :type log_str: str
        :param log_object: Where the log from.
        """
        try:
            if self.__LOG_LEVEL_DIC[log_level] < self.__LOG_LEVEL_DIC[self.__log_level]:
                return
            log_str = str(log_str)
            if not log_object.startswith("["):
                log_object = "[" + log_object
            if not log_object.endswith("]"):
                log_object = log_object + "]"
            if log_str != "" and log_str != "\n":
                if self.isLogToFile and self.logFile:
                    self.logFile.write(self.__process_log_string(log_level, log_object + " " + log_str)
                        + "\n")
                    if self.instantMode:
                        self.logFile.flush()
                else:
                    print(
                        self.__process_log_string(log_level, log_object + " " + log_str)
                        )
        except Exception as e:
            print(f"Logging error: {e}")
            print(f"Original message: [{log_level}] [{log_object}] {log_str}")

    # Log4j style logging method

    def fatal(self, log_str : str, log_object = "[Logger]"):
        self.log("F", log_str, log_object)

    def error(self, log_str : str, log_object = "[Logger]"):
        self.log("E", log_str, log_object)

    def warn(self, log_str : str, log_object = "[Logger]"):
        self.log("W", log_str, log_object)

    def info(self, log_str : str, log_object = "[Logger]"):
        self.log("I", log_str, log_object)

    def debug(self, log_str : str, log_object = "[Logger]"):
        self.log("D", log_str, log_object)

    def trace(self, log_str : str, log_object = "[Logger]"):
        self.log("T", log_str, log_object)
    
    def set_log_level(self, target_level : str):
        self.__log_level = target_level
    
    def set_should_attach_time(self, should_attach_time : bool):
        self.__shouldAttachTime = should_attach_time