import configparser
import requests

from datetime import datetime

from conf_path import conf_path

from .HelperFunctions import HelperFunctions as HF
from .ResponseParser import ResponseParser as RP

from .DataClasses import RedditRateLimit

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

#Auth refresh not rate limit since way above generouse for our use case
class RedditAuth:
    __access_token:str  #string containing acces token to later use
    __token_type:str    #name of token type
    __expires:datetime  #token expiration time in seconds
    __scope:str         #scope of what the token is allowed to do

    def __init__(self):
        config = configparser.ConfigParser()
        config._interpolation = configparser.ExtendedInterpolation()
        config.read(conf_path)
        self.config = config
        self.rl = RedditRateLimit()
        self.__refresh_token()

    def __str__(self):
        return f"RedditAuth( access_token: {self.__access_token}, scope: {self.__scope}, token_type: {self.__token_type}, expires:{self.__expires} GMT"

    # SOCKET WRAPPER FOR POST
    def __reddit_api_post(self, url:str, headers=None, data=None, auth = None):
        self.rl.check()
        resp = requests.post(url, data=data, headers=headers, auth=auth)
        (usd,rmain,restt) = RP.parse_reset_rate_limit(resp.headers)
        self.rl.update(usd,rmain,restt)
        Log.log("Auth token requests rate limit updated --- {}".format(self.rl.__str__()),DEBUG)
        return resp


    def __refresh_token(self):
        url = self.config["REDDIT"]["auth_url"]
        headers = {"User-Agent": self.config["REDDIT"]["user_agent"]}
        post_data = {"grant_type": "refresh_token",
                     "refresh_token": self.config["REDDIT_ACCES_TOKEN"]["t"]}
        client_auth = requests.auth.HTTPBasicAuth(self.config["REDDIT"]["client_id"],
                                                  self.config["REDDIT"]["client_secret"])
        resp = self.__reddit_api_post(url, headers, post_data, client_auth)
        data = resp.json()
        if resp.status_code != 200:
            msg = f"Got bad status code from req: {resp.status_code}, {resp.reason}"
            Log.log(msg,ERROR)
            raise Exception(msg)
        else:
            self.__access_token = data["access_token"]
            self.__token_type = data["token_type"]
            self.__expires = HF.derive_expire_time(data["expires_in"], resp.headers["Date"])
            self.__scope = data["scope"]
            Log.log("Refreshed the reddit auth token",GOOD)
            Log.log("New acces token",DEBUG, body=self.__str__())


    def __is_expired(self):
        """Get if token has reached its expiration time"""
        if self.__expires == None:
            raise Exception("Expires has not yet been set")
        to_ret = self.__expires <= datetime.utcnow()
        Log.log("Checking if auth has expired, comparing token: {} and our time {}. RES: {}".format(self.__expires, datetime.utcnow(), to_ret), INFO)
        return

    def get_formated_access_token(self):
        """Get access token, implicitly refreses it if expired"""
        if self.__access_token == None:
            raise Exception("Access token is None")
        if self.__is_expired():
            Log.log("RedditAuth has expired {}, our own clock: {}".format(self.__expires, datetime.utcnow()),DEBUG)
            self.__refresh_token()
        return f"{self.__token_type} {self.__access_token}"
