#!/usr/bin/python3
import json
import traceback

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

from datetime import datetime, timedelta

from Reddit.APIWrapper import APIWrapper as RedditAPIWrapper
from Reddit.Saver import RedditSaver
from Reddit.PromotedSaver import PromotedSaver

from Pushshift.Saver import PushshiftSaver

import itertools

from matplotlib import pyplot as plt

##################################################
raw = RedditAPIWrapper() #API WRAPPER

rs = RedditSaver()
##################################################
### MAIN SCRIPTS ###
####################

#Reduce these scraper functions


def search_scrape_algorithm():
    keywords = ["privacy", "security", "society", "economy"]
    #Create all combinations of the above keywords
    combinations = list( itertools.chain(*map(lambda y: itertools.combinations(keywords, y), range(1, len(keywords)+1))) )
    qs = ["chatGPT AND {}".format(" AND ".join(c)) for c in combinations]

    tot = 0

    for i in qs:
        for ii in ["all", "hour", "day", "week", "month", "year"]:
            for iii in ["relevance", "hot", "top", "new", "comments"]:
                data = raw.search_req(i,ii,iii) #Calls given api action
                Log.log("Recived {} data".format(len(data)), GOOD)
                tot = tot + len(data)
                for d in data:
                    rs.save(d)
    Log.log(f"SEARCH_SCRAPE_ALGORITHM DONE, found {tot} posts", GOOD)


def count_replies(root, depth):
    if depth <= 0:
        return 0

    repl = len(root.replies)
    for r in root.replies:
        repl += count_replies(r, depth-1)
    return repl

def load_comments():
    data = rs.load_all()
    for d in data:
        try:
            replies = raw.get_comments(d.id)
            d.replies = replies
            raw.fill_comments(d)
            #rc = count_replies(data[n])
            #print("\n count replies:", rc)
            rs.save(d)
        except Exception as e:
            Log.log("Bad happned when fetching comments: {}".format(e), WARNING)
            #traceback.print_exc()
            continue


def foo():
    reddit_data = rs.load_all()
    pss = PushshiftSaver()
    ps_data = pss.load_all()

    uid = set([d.id for d in reddit_data])
    ps_uid = set([d.id for d in ps_data])
    rest_left = ps_uid.difference(uid)

    Log.log("Promoting {} data".format(rest_left), DEBUG)

    to_promote = [d for d in ps_data if d.id in rest_left]

    res = raw.promote_ps(to_promote)


    proms = PromotedSaver()
    for r in res:
        raw.fill_comments(r)
        proms.save(r)
        #break

def bar():
    rep1 = []
    rep2 = []
    proms = PromotedSaver()
    prom = proms.load_all()
    #print(prom[0])

    for i in prom:
        #print(i)
        rep1.append(count_replies(i, 10000))
        rep2.append(count_replies(i, 3))

    data = rs.load_all()
    for i in data:
        #print(i)
        rep1.append(count_replies(i, 10000))
        rep2.append(count_replies(i, 3))

    #print(len(rep))
    #plt.hist(rep, bins=100)
    #plt.yscale("log")
    #plt.show()

    print(sum(rep1), sum(rep2))


if __name__ == "__main__":
    #search_scrape_algorithm()
    #load_comments()

    #foo()
    bar()

    #print(temp())
