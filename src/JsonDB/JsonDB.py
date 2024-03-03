#import STUFF

import os
import json

class JsonDB:
    def __init__(self, db_path):
        self.__path = db_path
        if not os.path.exists(self.__path):
            os.makedirs(self.__path)

    def __write_to_file(self, key:str, data):
        #path = os.path.join(db_path,key()
        path = os.path.join(self.__path, f"{key}.json")
        with open(path, "w") as outfile:
            json.dump(data.to_json(), outfile)

    def __read_from_file(self, file_name, t):
        path = os.path.join(self.__path, file_name)
        with open(path, "r") as infile:
            data = infile.read()
            data = json.loads(data)
            return t.from_json(data)

    def save(self, key:str, data):
        #if not self._exists(key):
        self.__write_to_file(key,data)


    def load_all(self, t):
        to_ret = []
        _, _, files = next(os.walk(self.__path))
        for f in files:
            to_ret.append( self.__read_from_file(f,t))
        return to_ret


    def _exists(self, key):
        _, _, files = next(os.walk(self.__path))
        return f"{key}.json" in files
