import json

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

from .DataClasses import ReditAward,ReditPost, ReditComment,ReditMore
from .HelperFunctions import HelperFunctions as HF

class ResponseParser:
    """Reddit specific parser functions"""

    @staticmethod
    def _parse_awards_response(awards_dict):
        n_awards = []
        for award in awards_dict:
            n_awards.append( ReditAward(
                giver_coin_reward = award["giver_coin_reward"],
                coin_price = award["coin_price"],
                id = award["id"],
                award_sub_type = award["award_sub_type"],
                coin_reward = award["coin_reward"],
                icon_url = award["icon_url"],
                days_of_premium = award["days_of_premium"],
                description = award["description"],
                subreddit_coin_reward = award["subreddit_coin_reward"],
                count = award["count"],
                name = award["name"],
                award_type = award["award_type"],
                static_icon_url = award["static_icon_url"]
            ))
        return n_awards

    @staticmethod
    def parse_search_query_response(j_dict):
        """Parses the raw dict that we get from the search endpoint"""
        result_count = j_dict["data"]["dist"]
        after = j_dict["data"]["after"]
        to_ret = []
        for c in j_dict["data"]["children"]:
            data = c["data"]
            n_awards = ResponseParser._parse_awards_response(data["all_awardings"])
            to_ret.append(ReditPost(
                subreddit = data["subreddit"],
                selftext = data["selftext"],
                title = data["title"],
                downs = data["downs"],
                upvote_ratio = data["upvote_ratio"],
                ups = data["ups"],
                total_awards_received = data["total_awards_received"],
                score = data["score"],
                edited = data["edited"],
                subreddit_type = data["subreddit_type"],
                created = HF.unix_to_datetime(data["created"]),
                allow_live_comments = data["allow_live_comments"],
                likes = data["likes"],
                view_count = data["view_count"],
                over_18 = data["over_18"],
                all_awardings = n_awards,
                spoiler = data["spoiler"],
                locked = data["locked"],
                id = data["id"],
                subreddit_id = data["subreddit_id"],
                num_comments = data["num_comments"],
                send_replies = data["send_replies"],
                whitelist_status = data["whitelist_status"],
                permalink = data["permalink"],
                created_utc = HF.unix_to_datetime(data["created_utc"]),
                subreddit_subscribers = data["subreddit_subscribers"],
                num_crossposts = data["num_crossposts"]
            ))
            Log.log("parse_search_query_response",
                    INFO,
                    f"RESULT_COUNT: {result_count}\nDATA: {to_ret}\nAFTER: {after}")
        return result_count, to_ret, after

    @staticmethod
    def parse_reset_rate_limit(headers):
        """Parses the raw dict that we get from the search endpoint"""
        to_ret = (int(float(headers["x-ratelimit-used"])),
                  int(float(headers["x-ratelimit-remaining"])),
                  HF.derive_refresh_time(int(headers["x-ratelimit-reset"]),
                                         headers["Date"]))
        Log.log(f"parse_rate_limit: {to_ret}",INFO)

        return to_ret

    @staticmethod
    def _more_parser(more_response_data):
        data = more_response_data["data"]
        to_ret = ReditMore(
            count = data["count"],
            name = data["name"],
            id = data["id"],
            parent_id = data["parent_id"],
            depth = data["depth"],
            children = data["children"]
        )
        Log.log("_more_parser",
            INFO,
            f"DATA: {to_ret}")
        return to_ret

    @staticmethod
    def _inner_comment_parser(inner_comment_response_data):
        inner_comments = inner_comment_response_data["data"]["children"]
        to_ret = []
        for c in inner_comments:
            if c["kind"] == "more":
                to_ret.append(ResponseParser._more_parser(c))
            else:
                data = c["data"]
                n_awards = ResponseParser._parse_awards_response(data["all_awardings"])
                to_ret.append(ReditComment(
                    replies = [] if data["replies"] == "" or data["replies"] is None else ResponseParser._inner_comment_parser(data["replies"]),
                    id = data["id"],
                    created_utc = HF.unix_to_datetime(data["created_utc"]),
                    parent_id = data["parent_id"],
                    score = data["score"],
                    all_awardings = n_awards,
                    collapsed = data["collapsed"],
                    body = data["body"],
                    edited = data["edited"],
                    name = data["name"],
                    downs = data["downs"],
                    stickied = data["stickied"],
                    permalink = data["permalink"],
                    locked = data["locked"],
                    created = HF.unix_to_datetime(data["created"]),
                    link_id = data["link_id"],
                    controversiality = data["controversiality"],
                    depth = data["depth"],
                    ups = data["ups"]
                ))
        Log.log("_inner_comment_parser",
                INFO,
                f"DATA: {to_ret}")
        return(to_ret)

    @staticmethod
    def parse_comments_query_response(response_data):
        return ResponseParser._inner_comment_parser(response_data[1])



    @staticmethod
    def parse_more_query_response(more_data):
        to_ret = []
        inner_comments = more_data["json"]["data"]["things"]
        for c in inner_comments:
            if c["kind"] == "more":
                to_ret.append(ResponseParser._more_parser(c))
            else:
                data = c["data"]
                n_awards = ResponseParser._parse_awards_response(data["all_awardings"])
                to_ret.append(ReditComment(
                    replies = [] if data["replies"] == "" or data["replies"] is None else ResponseParser.parse_more_query_response(data["replies"]),
                    id = data["id"],
                    created_utc = HF.unix_to_datetime(data["created_utc"]),
                    parent_id = data["parent_id"],
                    score = data["score"],
                    all_awardings = n_awards,
                    collapsed = data["collapsed"],
                    body = data["body"],
                    edited = data["edited"],
                    name = data["name"],
                    downs = data["downs"],
                    stickied = data["stickied"],
                    permalink = data["permalink"],
                    locked = data["locked"],
                    created = HF.unix_to_datetime(data["created"]),
                    link_id = data["link_id"],
                    controversiality = data["controversiality"],
                    depth = data["depth"],
                    ups = data["ups"]
                ))
        Log.log("parse_more_query_response",
                INFO,
                f"DATA: {to_ret}")
        return(to_ret)

    @staticmethod
    def promote_parser(promoted):
        data = promoted[0]["data"]["children"][0]["data"]
        n_awards = ResponseParser._parse_awards_response(data["all_awardings"])
        return ReditPost(
            subreddit = data["subreddit"],
            selftext = data["selftext"],
            title = data["title"],
            downs = data["downs"],
            upvote_ratio = data["upvote_ratio"],
            ups = data["ups"],
            total_awards_received = data["total_awards_received"],
            score = data["score"],
            edited = data["edited"],
            subreddit_type = data["subreddit_type"],
            created = HF.unix_to_datetime(data["created"]),
            allow_live_comments = data["allow_live_comments"],
            likes = data["likes"],
            view_count = data["view_count"],
            over_18 = data["over_18"],
            all_awardings = n_awards,
            spoiler = data["spoiler"],
            locked = data["locked"],
            id = data["id"],
            subreddit_id = data["subreddit_id"],
            num_comments = data["num_comments"],
            send_replies = data["send_replies"],
            whitelist_status = data["whitelist_status"],
            permalink = data["permalink"],
            created_utc = HF.unix_to_datetime(data["created_utc"]),
            subreddit_subscribers = data["subreddit_subscribers"],
            num_crossposts = data["num_crossposts"]
        )
