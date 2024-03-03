#Imports
import configparser
from datetime import datetime

#Log module globals
ALL = 6
#
INFO = 5
DEBUG = 4
GOOD = 3
WARNING = 2
ERROR = 1
#
NONE = 0

Fgr_Reset = "\x1b[0m"

Fgr_Default = "\x1b[39m"
Fgr_Red = "\x1b[31m"
Fgr_Blue = "\x1b[34m"
Fgr_Yellow = "\x1b[33m"
Fgr_Green = "\x1b[32m"

color_mapper = {
    INFO: Fgr_Default,
    DEBUG: Fgr_Blue,
    GOOD: Fgr_Green,
    WARNING: Fgr_Yellow,
    ERROR: Fgr_Red
}

tag_mapper = {
    INFO: "INFO",
    DEBUG: "DEBUG",
    GOOD: "GOOD",
    WARNING: "WARNING",
    ERROR: "ERROR"
}

class Logger:
    @staticmethod
    def _write(text:str, body:str):
        if log_file_path is not None:
            with open(log_file_path, "a+") as f:
                f.write(text+"\n")
                if body is not None:
                    f.write(body+"\n")

    @staticmethod
    def _terminal(text:str, log_level:int, body:str):
        if terminal_color_on:
            print(f"{color_mapper[log_level]}{text}{Fgr_Reset}")
            if body is not None:
                print(f"{color_mapper[log_level]}{body}{Fgr_Reset}")
        else:
            print(text)
            if body is not None:
                print(body)

    @staticmethod
    def log(text:str, log_level:int = INFO, body:str=None):
        if log_level <= set_log_level:
            time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            msg = f"{time} {tag_mapper[log_level]:<7}: {text}"
            Logger._terminal(msg, log_level, body)
            Logger._write(msg,body)


#TRY: Load config file and set modules varible
try:
    config = configparser.ConfigParser()
    config._interpolation = configparser.ExtendedInterpolation()
    from conf_path import conf_path
    config.read(conf_path)
    log_file_path = config["LOG"]["path"]
    set_log_level = config["LOG"].getint("level")
    terminal_color_on = config["LOG"].getboolean("terminal_color")

except Exception as e:
    log_file_path = None
    set_log_level = INFO
    terminal_color_on = True
    Logger.log("Could not set up Logger",ERROR,e)



##################################################
if __name__ == "__main__":
    #Logger.log("Def")
    Logger.log("INFO    asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad",INFO)
    Logger.log("DEBUG   asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad",DEBUG)
    Logger.log("GOOD    asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad",GOOD)
    Logger.log("WARNING asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad",WARNING)
    Logger.log("ERROR   asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad",ERROR)
    print()
    Logger.log("INFO",INFO, body = "asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad")
    Logger.log("DEBUG",DEBUG, body = "asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad")
    Logger.log("GOOD",GOOD, body = "asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad")
    Logger.log("WARNING",WARNING, body = "asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad")
    Logger.log("ERROR",ERROR, body = "asd asdadasd asdadasd asdasd asd asd asdasad asdaasd sad")
