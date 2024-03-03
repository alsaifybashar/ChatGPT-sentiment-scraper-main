import os
import configparser

from conf_path import conf_path

from JsonDB.JsonDB import JsonDB

from dataclasses import is_dataclass

from .DataClasses import ReditAward, ReditPost



class PromotedSaver(JsonDB):
    def __init__(self):
        config = configparser.ConfigParser()
        config._interpolation = configparser.ExtendedInterpolation()
        config.read(conf_path)
        db_path = config["DB"]["path"]
        pushshift_db_path = os.path.join(db_path, "promoted")
        super().__init__(pushshift_db_path)

    def __key(self,data:ReditPost):
        return data.subreddit_id+"-"+data.id

    def save(self,data:ReditPost):
        super().save(self.__key(data),data)

    def load_all(self):
        return super().load_all(ReditPost)
