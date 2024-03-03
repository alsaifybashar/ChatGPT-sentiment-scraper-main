#Imports
import json
import time
import configparser
import urllib

from datetime import datetime, timedelta

import requests

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

from .DataClasses import PushshiftRateLimit
from .HelperFunctions import HelperFunctions as HF

from .ResponseParser import ResponseParser as RP

from conf_path import conf_path

##################################################
class APIWrapper:
    def __init__(self):
        config = configparser.ConfigParser()
        config._interpolation = configparser.ExtendedInterpolation()
        config.read(conf_path)
        self.config = config
        #
        self.r_session = requests.Session()
        self.rl = PushshiftRateLimit()

    def __url_parse(self, path, query=None, safe=""):
        o = urllib.parse.ParseResult(
            scheme = "https",
            netloc = "api.pushshift.io",
            path = path,
            params = "",
            query = urllib.parse.urlencode(query,safe=safe) if query is not None else "",
            fragment = "")
        url = urllib.parse.urlunparse(o)
        Log.log(f"Url parsed {url}")
        return url

    # SOCKET WRAPPER FOR GET
    def _api_get(self, path, query=None, headers=None):
        url = self.__url_parse(path, query, safe="!+:")
        #Wait till we have rl avalible
        self.rl.check()
        Log.log("Requests rate limit updated --- {}".format(self.rl.__str__()),DEBUG)
        #Do reqquest
        resp = self.r_session.get(url, headers=headers)
        #Parse status code
        if resp.status_code != 200:
            msg = f"Got bad status code from req: {resp.status_code}, {resp.reason}"
            Log.log(msg,ERROR)
            raise Exception(msg)
        elif resp.json()["error"] is not None:
            Log.log(resp.json()["error"],ERROR, resp.json()["metadata"])
            raise Exception("Error")
        else:
            return resp

    def search_query(self, q:str, after:datetime, before:datetime):
        path = "reddit/submission/search/"
        query = {"q":q,
                 "size":500,
                 "after":HF.datetime_to_unix(after),
                 "before":HF.datetime_to_unix(before)
                 }
        #
        resp = self._api_get(path, query)
        data = resp.json()
        return RP.parse_search_query_response(data)

    def t(self):
        path = "reddit/submission/search/"
        query = {"q":"chatGPT",
                 "size":1,
                 "after":HF.datetime_to_unix(datetime(year=2022, month=11, day=30)),
                 "before":HF.datetime_to_unix(datetime(year=2023, month=3, day=3))
                 }
        resp = self._api_get(path, query)
        data = resp.json()
        return RP.parse_search_query_response(data)
