#!/usr/bin/python3
import json

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

from datetime import datetime, timedelta

from Pushshift.APIWrapper import APIWrapper as PushshiftAPIWrapper
from Pushshift.Saver import PushshiftSaver

##################################################

paw = PushshiftAPIWrapper() #API WRAPPER
pss = PushshiftSaver()

##################################################

#If date interval exceded, halfs existing interval.
#If date interval not exceeded, shiotfts it forward one slot(curr time diff) and increses it by 1%
def _date_interval_window_algorithm(curr_window_start:datetime, curr_window_end:datetime, exceeded_window:bool = False):
    window_span = curr_window_end - curr_window_start
    if exceeded_window:
        reduction = window_span/2 #reduce span by half
        curr_window_end = (curr_window_start + reduction)
        if (reduction < timedelta(seconds=1)): #if diff span less then 1 sec set it to 1 sec
            curr_window_end = curr_window_start + timedelta(seconds=1)
            Log.log(f"Exceeded date interval window, min resulution reached setting it to 1 day: {curr_window_start} -> {curr_window_end}", DEBUG)
        else:
            Log.log(f"exceeded date interval window, reducing it by 1/2: {curr_window_start} -> {curr_window_end}",DEBUG)
    else:
        inc = (window_span * 1.05)#increase span by 5%
        if inc < timedelta(seconds=1):#if inc smaller then 1 sec
            inc = timedelta(seconds=1)#inc by a whole second
        else:
            curr_window_start = curr_window_end
            curr_window_end = curr_window_end + inc
        Log.log(f"Date interval window not exceeded, moving intervall forward and increaseing it to: {curr_window_start} -> {curr_window_end}", DEBUG)
    return curr_window_start, curr_window_end


##################################################
### MAIN SCRIPTS ###
####################

#Reduce these scraper functions


def search_scrape_algorithm(q):
    start_date  = datetime(year=2022, month=11, day=30) #(inclusive) #TODO: move to conf
    end_date = datetime(year=2023, month=3, day=3) #(exclusive) #TODO: move to conf
    limit = 450 #TODO: move to conf

    curr_from = start_date
    curr_to = end_date

    tot = 0

    while True:
        data = paw.search_query(q, curr_from,curr_to)
        if len(data) > limit:
            Log.log("Found {} repos, exceeded limit {}, reducing window".format(len(data), limit), WARNING)
            curr_from, curr_to = _date_interval_window_algorithm(curr_from, curr_to, exceeded_window = True)
            continue
        else:
            Log.log("Found {} repos, saving them".format(len(data)), GOOD)
            tot = tot + len(data)
            for d in data:
                pss.save(d)
            curr_from, curr_to = _date_interval_window_algorithm(curr_from, curr_to)
            if end_date < curr_from: #If we have reached end date
                break
    Log.log(f"SEARCH_SCRAPE_ALGORITHM DONE, found {tot} posts", WARNING)

if __name__ == "__main__":
    qs = ["chatGPT+privacy",
          "chatGPT+security",
          "chatGPT+society",
          "chatGPT+economy"]

    #for q in qs:
    #    search_scrape_algorithm(q)

    print(len(pss.load_all()))
