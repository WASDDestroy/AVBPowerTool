'''
LogUtils provides log ability for programs. Destination can be manually assigned in __init__().

log(): Log a string to destination you assigned when an instance is created.

setLogLevel(): Set when should LogUtils *starts* to log it to destination. 

:author: WASD_Destroy
'''
import sys, time, os

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


    # Determine log destination, console is the default option.
    def __init__(self,
                 output = "file",
                 shouldAttachTime = False,
                 logDir = None,
                 instantMode = False) -> None:
        self.instantMode = instantMode
        self.isLogToFile = True
        self.__shouldAttachTime = shouldAttachTime
        if logDir is None:
            logDir = os.path.join(os.getcwd(), "Logs")
        if output.lower() != "console":
            try:
                if not os.path.exists(logDir):
                    os.makedirs(logDir, exist_ok=True)
                fileName = os.path.join(logDir,
                                        "log_" + time.strftime("%Y%m%d_%H%M%S", time.localtime()) + ".log")
                self.logFile = open(fileName, "w+", encoding = "UTF-8")
                self.isLogToFile = True
                print(f"Log file created at: {fileName}")
            except PermissionError:
                print(f"Warning: Cannot create log directory at {logDir}, falling back to console output")
                self.isLogToFile = False
            except Exception as e:
                print(f"Warning: Error creating log file: {e}, falling back to console output")
                self.isLogToFile = False
        try:
            self.log("I", "Logger instance created.", "LogUtils")
        except:
            print("[INFO] [LogUtils] Logger instance created.")
    
    def __del__(self) -> None:
        if hasattr(self, 'logFile') and self.logFile:
            try:
                self.logFile.close()
            except:
                pass

    # Construct log strings
    def __constructTrace(self, verboseStr):
        tmpStr = ""
        if self.__shouldAttachTime:
            tmpStr = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[TRACE] " + tmpStr + verboseStr

    def __constructDebug(self, debugStr):
        tmpStr = ""
        if self.__shouldAttachTime:
            tmpStr = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[DEBUG] " + tmpStr + debugStr

    def __constructInfo(self, infoStr):
        tmpStr = ""
        if self.__shouldAttachTime:
            tmpStr = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[INFO] " + tmpStr + infoStr
    
    def __constructWarn(self, warnStr):
        tmpStr = ""
        if self.__shouldAttachTime:
            tmpStr = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[WARN] " + tmpStr + warnStr
    
    def __constructError(self, errorStr):
        tmpStr = ""
        if self.__shouldAttachTime:
            tmpStr = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[ERROR] " + tmpStr + errorStr
    
    def __constructFatal(self, errorStr):
        tmpStr = ""
        if self.__shouldAttachTime:
            tmpStr = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] "
        return "[FATAL] " + tmpStr + errorStr
    
    def __processLogString(self, logLevel : str, logStr : str) -> str:
        logLevel = logLevel.upper()[0]
        logInfo = ""
        if logLevel == "T" or logLevel == "V": # Back-compatible
            logInfo = self.__constructTrace(logStr)
        elif logLevel == "D":
            logInfo = self.__constructDebug(logStr)
        elif logLevel == "I":
            logInfo = self.__constructInfo(logStr)
        elif logLevel == "W":
            logInfo = self.__constructWarn(logStr)
        elif logLevel == "E":
            logInfo = self.__constructError(logStr)
        elif logLevel == "F":
            logInfo = self.__constructFatal(logStr)
        else:
            logInfo = self.__constructWarn(logStr) \
                + " (Log level not specified or typo mistake)"
        return logInfo
    
    def log(self, logLevel : str, logStr : str, logObject = "[Logger]"):
        '''
        log() provides constant log realization for all scripts.
        
        Format: `[Log Level] [Log Object] [Time] <Log Content>`

        Empty <Log Content> string or "\\n" will be ignored.
        
        :param logLevel: Determine your log's level, V,D,I,W,E(non-case-sensitive)
        or any string start with these 5 letters are accepted. Default value is W.
        :type logLevel: str
        :param logStr: Log content. Will get empty output if type `\\n` or keep it empty
        :type logStr: str
        :param logObject: Where the log from.
        '''
        try:
            if self.__LOG_LEVEL_DIC[logLevel] < self.__LOG_LEVEL_DIC[self.__log_level]:
                return
            logStr = str(logStr)
            if not logObject.startswith("["):
                logObject = "[" + logObject
            if not logObject.endswith("]"):
                logObject = logObject + "]"
            if logStr != "" and logStr != "\n":
                if self.isLogToFile and self.logFile:
                    self.logFile.write(self.__processLogString(logLevel, logObject + " " + logStr)
                        + "\n")
                    if self.instantMode:
                        self.logFile.flush()
                else:
                    print(
                        self.__processLogString(logLevel, logObject + " " + logStr)
                        )
        except Exception as e:
            print(f"Logging error: {e}")
            print(f"Original message: [{logLevel}] [{logObject}] {logStr}")
    
    def setLogLevel(self, targetLevel : str):
        self.__log_level = targetLevel
    
    def setShouldAttachTime(self, shouldAttachTime : bool):
        self.__shouldAttachTime = shouldAttachTime