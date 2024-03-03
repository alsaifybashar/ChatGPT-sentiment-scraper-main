from datetime import datetime, timedelta

from dataclasses import dataclass, asdict

from .HelperFunctions import HelperFunctions as HF

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

#TODO: make thread safe?
class PushshiftRateLimit:
    used:int        #Used req
    maximum:int     #Max request per min
    reset:datetime  #Self enforced reset time

    def __init__(self):
        self.maximum = 60 #Move to conf
        self.__reset()

    def __str__(self):
        return f"Used: {self.used}/{self.maximum} Resets: {self.reset} GMT"

    def __reset(self):
        self.used = 0
        self.reset = datetime.now() + timedelta(minutes=1)

    def __inc(self):
        self.used = self.used + 1

    def check(self):
        """Blocking till we get request avalible"""
        if self.reset < datetime.now():# if we have passed reset
            self.__reset()
            self.__inc()
        else:
            if self.used >= self.maximum: #If we have no remaining
                Log.log(f"Sleeping to: {self.reset}",DEBUG)
                HF.sleep_to(self.reset)
                Log.log(f"Done sleeping",DEBUG)
                self.__reset()
                self.__inc()
            else:
                self.__inc()


@dataclass
class PushShiftPost:
    subreddit:str
    selftext:str
    title:str
    subreddit_id:str
    id:str
    permalink:str
    created_utc:datetime
    retrieved_utc:datetime
    updated_utc:datetime

    def to_json(self):
        return {
            "subreddit": self.subreddit,
            "selftext": self.selftext,
            "title": self.title,
            "subreddit_id": self.subreddit_id,
            "id": self.id,
            "permalink": self.permalink,
            "created_utc": HF.datetime_to_unix(self.created_utc),
            "retrieved_utc": HF.datetime_to_unix(self.retrieved_utc),
            "updated_utc": HF.datetime_to_unix(self.updated_utc),
    }

    @staticmethod
    def from_json(dct):
        return PushShiftPost(
            dct["subreddit"],
            dct["selftext"],
            dct["title"],
            dct["subreddit_id"],
            dct["id"],
            dct["permalink"],
            HF.unix_to_datetime(dct["created_utc"]),
            HF.unix_to_datetime(dct["retrieved_utc"]),
            HF.unix_to_datetime(dct["updated_utc"])
        )
