from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

from .DataClasses import PushShiftPost
from .HelperFunctions import HelperFunctions as HF

class ResponseParser:
    """Reddit specific parser functions"""

    @staticmethod
    def parse_search_query_response(in_data):
        """Parses the raw dict that we get from the search endpoint"""
        to_ret = []
        for data in in_data["data"]:
            to_ret.append(
                PushShiftPost(
                    subreddit = data["subreddit"],
                    selftext = data["selftext"],
                    title = data["title"],
                    subreddit_id = data["subreddit_id"],
                    id = data["id"],
                    permalink = data["permalink"],
                    created_utc = HF.unix_to_datetime(data["created_utc"]),
                    retrieved_utc = HF.unix_to_datetime(data["retrieved_utc"]),
                    updated_utc = HF.unix_to_datetime(data["updated_utc"])
                )
            )
            Log.log("parse_search_query_response",
                    INFO,
                    f"DATA: {to_ret}")
        return to_ret
