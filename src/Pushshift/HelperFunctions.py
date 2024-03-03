from datetime import datetime,timedelta

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

class HelperFunctions:
    """
    Functinos that the rest of the script on this module level can utalize
    """

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
