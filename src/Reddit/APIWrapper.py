#Imports
import json
import time
import configparser
import urllib

from datetime import datetime, timedelta

import requests
import requests.auth

from .RedditAuth import RedditAuth
from .DataClasses import RedditRateLimit
from .HelperFunctions import HelperFunctions as HF
from .ResponseParser import ResponseParser as RP

from .DataClasses import ReditMore

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

from conf_path import conf_path

fetched = set()


##################################################
class APIWrapper:
    def __init__(self):
        config = configparser.ConfigParser()
        config._interpolation = configparser.ExtendedInterpolation()
        config.read(conf_path)
        self.config = config
        #
        self.auth = RedditAuth()
        self.r_session = requests.Session()
        self.rl = RedditRateLimit()

    # SOCKET WRAPPER FOR GET
    def _reddit_api_get(self, url:str, headers=None, query=None):
        req_hdrs = {"Authorization": self.auth.get_formated_access_token(),
                'User-agent': self.config["REDDIT"]["user_agent"]}
        headers = req_hdrs if headers is None else headers.update(req_hdrs)
        #Wait till we have rl avalible
        self.rl.check()
        #Do reqquest
        Log.log(f"Requesting url {url}", DEBUG)
        resp = self.r_session.get(url, headers=headers)
        #Parse status code
        if resp.status_code != 200:
            msg = f"Got bad status code from req: {resp.status_code}, {resp.reason}"
            Log.log(msg ,ERROR)
            raise Exception(msg)
        else:
            #Fix remaining req and reset time
            (usd,rmain,restt) = RP.parse_reset_rate_limit(resp.headers)
            self.rl.update(usd,rmain,restt)
            Log.log("Requests rate limit updated --- {}".format(self.rl.__str__()),DEBUG)
            #Return result
            return resp

    def _get_wrapper(self, path, query):
        o = urllib.parse.ParseResult(
            scheme = "https",
            netloc = "oauth.reddit.com",
            path = path,
            params = "",
            query = urllib.parse.urlencode(query, quote_via=urllib.parse.quote, safe=" ,"),
            fragment = "")
        url = urllib.parse.urlunparse(o)
        return self._reddit_api_get(url, query = query)

    # SEARCH ##################################################

    def search_req(self, q, time, sort):
        path = "search.json"
        query = {"q":q,
                 "limit":100,
                 "sort":sort,
                 "t":time}

        resp = self._get_wrapper(path, query)
        j_data = resp.json()
        _, to_ret, after = RP.parse_search_query_response(j_data)
        data = to_ret

        while after is not None:
            query["after"] = after
            resp = self._get_wrapper(path, query)
            j_data = resp.json()
            _, to_ret, after = RP.parse_search_query_response(j_data)
            data = data + to_ret
        return data

    # COMMENTS ##################################################

    def get_comments(self, post_id:str):
        path = f"comments/{post_id}.json"
        #TODO: 1 should be 100
        query = {"depth":1000,
                 "limit":100
                 }

        resp = self._get_wrapper(path, query)
        j_data = resp.json()
        comments = RP.parse_comments_query_response(j_data)
        #comments may contain 'more' clauses

        #print(json.dumps(resp.json(), indent=4)) #TODO: remove
        return comments

    # MORE ##################################################
    def fill_comments(self, post):
        filled_replies = self.saturate_more(post,f"t3_{post.id}")
        post.replies = filled_replies


    def construct_tree(self,replies): #list of replies
        #print("# REPLIES #", replies)

        def find_parrent(leaf, tree):
            for t in tree: #t is reditcomment
                if leaf.parent_id == t.name:
                    return t
                else:
                    if type(t) != ReditMore:
                        res = find_parrent(leaf, t.replies)
                        if res is not None:
                            return res
                        else:
                            continue
                    else:
                        continue

        new_tree = []
        for r in replies:
            res = find_parrent(r, new_tree)
            if res is None:
                new_tree.append(r)
            else:
                res.replies.append(r)
        #print("# new_tree #", new_tree)
        return new_tree


    #saturate 'more' clauses
    def saturate_more(self, parent, post_id):
        filled_replies = []
        for c in parent.replies:
            #print("#C", c)
            if type(c) == ReditMore:
                #print("WAS REDDIT MORE")
                if c.id == "_":
                    continue
                #This is a 'more' clause
                res = self.get_more(post_id, c.children)
                #print("RES:", res)
                #res is list of post which may contain 'more'
                comment_tree = self.construct_tree(res)
                #print("FETCHED MORE, CONSTRUCTED TREE:", comment_tree)

                for root in comment_tree:
                    if type(root) == ReditMore:
                        #raise Exception("WTF")
                        continue
                    else:
                        tmp = self.saturate_more(root, post_id) #check THIS c replies
                        root.replies = tmp
                        filled_replies.append(root)
                        #print("ADDED FIXED NODE TO TREE", filled_replies)

            else:
                #print("WAS STANDARD")
                tmp = self.saturate_more(c, post_id) #check THIS c replies
                #print("filled replies:", tmp)
                c.replies = tmp
                filled_replies.append(c)
                #print("ADDED STANDARD:", filled_replies)
        return filled_replies





    def get_more(self, link_id, children_ids):
        rest = []
        if len(children_ids) > 100:
            Log.log("TO MANY CHILDREN TO FETCH MORE OF", WARNING)
            print("children_ids", children_ids)
            rest = children_ids[100:]
            children_ids = children_ids[:100]
            print("FETCHING",children_ids, len(children_ids))
            print("REST",rest, len(rest))

        if not fetched.isdisjoint(set(children_ids)):
            print()
            print("UNION",fetched.union(set(children_ids)))
            raise Exception("duplicate children fetched")
        else:
            fetched.update(set(children_ids))

        path = f"api/morechildren"
        query = {"depth":1000,
                 "limit":100,
                 "link_id": link_id,
                 "children": ",".join(children_ids),
                 "api_type": "json"
                 }
        to_ret = []
        resp = self._get_wrapper(path, query)
        #print(json.dumps(resp.json(), indent=4))

        data = resp.json()
        comments = RP.parse_more_query_response(data)
        #print(comments)
        to_ret = comments

        if len(rest) > 0:
            to_ret += self.get_more(link_id,rest)

        return to_ret

    # PROMOTE ##################################################
    def promote_ps(self, ps_list):
        to_ret = []
        for ps in ps_list:
            try:
                path = f"comments/{ps.id}.json"
                query = {"depth":1000,
                         "limit":100
                         }

                resp = self._get_wrapper(path, query)
                j_data = resp.json()
                #print(json.dumps(j_data, indent=4))

                #print()
                promoted = RP.promote_parser(j_data)
                #print(promoted)
                comments = RP.parse_comments_query_response(j_data)
                promoted.selftext = ps.selftext
                promoted.title = ps.title
                promoted.replies = comments
                to_ret.append(promoted)
                #break
            except Exception as e:
                Log.log("Bad happned when promoting ps: {}".format(e), WARNING)
                #traceback.print_exc()
                continue
        return to_ret
