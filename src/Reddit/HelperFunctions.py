import math
import time

from datetime import datetime,timedelta

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

class HelperFunctions:
    """
    Functinos that the rest of the script on this module level can utalize
    """
    @staticmethod
    def format_timestring(timestamp:str) ->datetime:
        """Reddit API specific helper, used to take reddits timestamp
        wich includes locale abriviation and derive a python datetime"""
        #WARNING, the below part depend on reddit api AND locale of python to decode time with
        date_and_time = timestamp.split(",")[1]#remove locale day abrivation
        to_ret = datetime.strptime(date_and_time, " %d %b %Y %H:%M:%S %Z")
        Log.log(f"HelperFunctions.format_timestring --- from '{timestamp}' to '{to_ret}'",INFO)
        return to_ret

    @staticmethod
    def derive_refresh_time(time:int ,timestamp:str) -> datetime:
        """Reddit API specific helper, used to deduse refresh time by taking refresh_in second and a reddit timestamp"""
        curr_time = HelperFunctions.format_timestring(timestamp)
        to_ret = curr_time + timedelta(seconds=time+1) # time of next refresh +1sec
        Log.log(f"HelperFunctions.derive_refresh_time --- used '{time}' and '{timestamp}' derived '{to_ret}'",INFO)
        return to_ret

    @staticmethod
    def derive_expire_time(time:int ,timestamp:str) -> datetime:
        """Reddit API specific helper, used to deduse expire time by taking expire_in second and  a reddit timestamp"""
        curr_time = HelperFunctions.format_timestring(timestamp)
        to_ret =  curr_time + timedelta(seconds=time-1)# time of expiration time -1sec
        Log.log(f"HelperFunctions.derive_expire_time --- used '{time}' and '{timestamp}' derived '{to_ret}'",INFO)
        return to_ret

    @staticmethod
    def sleep_to(to:datetime) -> None:
        """Sleep to given time (datetime) has arrived"""
        now = datetime.utcnow()
        to_sleep = math.ceil((to-now).total_seconds())
        #log("sleeping {} seconds, to {}".format(to_sleep, now+timedelta(seconds=to_sleep)))
        time.sleep(to_sleep)

    @staticmethod
    def unix_to_datetime(int_time) -> datetime:
        """Convert a unix timestamp to a python3 datetime"""
        to_ret =  datetime.fromtimestamp(int_time)
        Log.log(f"HelperFunctions.unix_to_datetime --- from '{int_time}' to '{to_ret}'",INFO)
        return to_ret

    @staticmethod
    def datetime_to_unix(time:datetime) -> int:
        """Convert a unix timestamp to a python3 datetime"""
        to_ret =  int(time.timestamp())
        Log.log(f"HelperFunctions.datetime_to_unix --- from '{time}' to '{to_ret}'",INFO)
        return to_ret
