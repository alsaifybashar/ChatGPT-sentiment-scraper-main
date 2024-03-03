import os
import configparser

from JsonDB.JsonDB import JsonDB

from dataclasses import is_dataclass

from .DataClasses import PushShiftPost

from conf_path import conf_path

class PushshiftSaver(JsonDB):
    def __init__(self):
        config = configparser.ConfigParser()
        config._interpolation = configparser.ExtendedInterpolation()
        config.read(conf_path)
        db_path = config["DB"]["path"]
        pushshift_db_path = os.path.join(db_path, "pushshift")
        super().__init__(pushshift_db_path)

    def __key(self,data):
        return data.subreddit_id+"-"+data.id

    def save(self,data:PushShiftPost):
        super().save(self.__key(data),data)

    def load_all(self):
        return super().load_all(PushShiftPost)
