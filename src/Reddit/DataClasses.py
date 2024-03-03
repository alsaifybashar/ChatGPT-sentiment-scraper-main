from datetime import datetime

from dataclasses import dataclass, asdict, field

from .HelperFunctions import HelperFunctions as RHF

from Logger.Logger import Logger as Log
from Logger.Logger import INFO,DEBUG,GOOD,WARNING,ERROR

class RedditRateLimit:
    used:int        #'x-ratelimit-used': '1',
    remaining:int   #'x-ratelimit-remaining': '299',
    reset:datetime  #'x-ratelimit-reset': '484', 'Date': 'Tue, 21 Feb 2023 15:31:56 GMT'

    def __init__(self):
        self.used = 0
        self.remaining=0
        self.reset=None

    def __str__(self):
        return f"Used: {self.used} Left: {self.remaining} Resets: {self.reset} GMT"

    def check(self):
        if self.reset is not None:
            if self.remaining <= 0: #If we have no remaining
                Log.log(f"Sleeping to: {self.reset}",DEBUG)
                RHF.sleep_to(self.reset)
                Log.log(f"Done sleeping",DEBUG)

    def update(self,u,rm,rt):
        self.used = u
        self.remaining = rm
        self.reset = rt


@dataclass
class ReditMore:
    count:int
    name:str
    id:str
    parent_id:str
    depth:int
    children: list[str]



@dataclass
class ReditAward:
    giver_coin_reward:bool
    coin_price:int
    id:str
    award_sub_type:str
    coin_reward:int
    icon_url:str
    days_of_premium:float
    description:str
    subreddit_coin_reward:int
    count:int
    name:str
    award_type:str
    static_icon_url:str

    def to_json(self):
        return {
            "giver_coin_reward": self.giver_coin_reward,
            "coin_price": self.coin_price,
            "id": self.id,
            "award_sub_type": self.award_sub_type,
            "coin_reward": self.coin_reward,
            "icon_url": self.icon_url,
            "days_of_premium": self.days_of_premium,
            "description": self.description,
            "subreddit_coin_reward": self.subreddit_coin_reward,
            "count": self.count,
            "name": self.name,
            "award_type": self.award_type,
            "static_icon_url": self.static_icon_url
        }

    @staticmethod
    def from_json(dct):
        return ReditAward(
            dct["giver_coin_reward"],
            dct["coin_price"],
            dct["id"],
            dct["award_sub_type"],
            dct["coin_reward"],
            dct["icon_url"],
            dct["days_of_premium"],
            dct["description"],
            dct["subreddit_coin_reward"],
            dct["count"],
            dct["name"],
            dct["award_type"],
            dct["static_icon_url"]
        )

@dataclass
class ReditComment:
    replies:list['ReditComment']
    id:str
    created_utc:datetime
    parent_id:str
    score:int
    all_awardings:list[ReditAward]
    collapsed:bool
    body:str
    edited:bool
    name:str
    downs:int
    stickied:bool
    permalink:str
    locked:str
    created:datetime
    link_id:str
    controversiality:float
    depth:int
    ups:int

    def to_json(self):
        return {
            "replies": [r.to_json() for r in self.replies],
            "id": self.id,
            "created_utc": RHF.datetime_to_unix(self.created_utc),
            "parent_id": self.parent_id,
            "score": self.score,
            "all_awardings": [a.to_json() for a in self.all_awardings],
            "collapsed": self.collapsed,
            "body": self.body,
            "edited": self.edited,
            "name": self.name,
            "downs": self.downs,
            "stickied": self.stickied,
            "permalink": self.permalink,
            "locked": self.locked,
            "created": RHF.datetime_to_unix(self.created_utc),
            "link_id": self.link_id,
            "controversiality": self.controversiality,
            "depth": self.depth,
            "ups": self.ups
        }

    @staticmethod
    def from_json(dct):
        return ReditComment(
            [ReditComment.from_json(r) for r in dct["replies"]],
            dct["id"],
            RHF.unix_to_datetime(dct["created_utc"]),
            dct["parent_id"],
            dct["score"],
            [ReditAward.from_json(a) for a in dct["all_awardings"]],
            dct["collapsed"],
            dct["body"],
            dct["edited"],
            dct["name"],
            dct["downs"],
            dct["stickied"],
            dct["permalink"],
            dct["locked"],
            RHF.unix_to_datetime(dct["created"]),
            dct["link_id"],
            dct["controversiality"],
            dct["depth"],
            dct["ups"]
        )

@dataclass
class ReditPost:
    subreddit:str
    selftext:str
    title:str
    downs:int
    upvote_ratio:float
    ups:int
    total_awards_received:int
    score:int
    edited:bool
    subreddit_type:str
    created:datetime
    allow_live_comments:bool
    likes:int
    view_count:int
    over_18:bool
    all_awardings:list[ReditAward]
    spoiler:bool
    locked:bool
    id:str
    subreddit_id:str
    num_comments:int
    send_replies:bool
    whitelist_status:str
    permalink:str
    subreddit_subscribers:int
    created_utc:datetime
    num_crossposts:int
    replies:list['ReditComment'] = field(default_factory=list)

    def to_json(self):
        return {
            "subreddit": self.subreddit,
            "selftext": self.selftext,
            "title": self.title,
            "downs": self.downs,
            "upvote_ratio": self.upvote_ratio,
            "ups": self.ups,
            "total_awards_received": self.total_awards_received,
            "score": self.score,
            "edited": self.edited,
            "subreddit_type": self.subreddit_type,
            "created": RHF.datetime_to_unix(self.created),
            "allow_live_comments": self.allow_live_comments,
            "likes": self.likes,
            "view_count": self.view_count,
            "over_18": self.over_18,
            "all_awardings": [a.to_json() for a in self.all_awardings],
            "spoiler": self.spoiler,
            "locked": self.locked,
            "id": self.id,
            "subreddit_id": self.subreddit_id,
            "num_comments": self.num_comments,
            "send_replies": self.send_replies,
            "whitelist_status": self.whitelist_status,
            "permalink": self.permalink,
            "subreddit_subscribers": self.subreddit_subscribers,
            "created_utc": RHF.datetime_to_unix(self.created_utc),
            "num_crossposts": self.num_crossposts,
            "replies": [r.to_json() for r in self.replies]
            }

    @staticmethod
    def from_json(dct):
        return ReditPost(
            dct["subreddit"],
            dct["selftext"],
            dct["title"],
            dct["downs"],
            dct["upvote_ratio"],
            dct["ups"],
            dct["total_awards_received"],
            dct["score"],
            dct["edited"],
            dct["subreddit_type"],
            RHF.unix_to_datetime(dct["created"]),
            dct["allow_live_comments"],
            dct["likes"],
            dct["view_count"],
            dct["over_18"],
            [ReditAward.from_json(a) for a in dct["all_awardings"]],
            dct["spoiler"],
            dct["locked"],
            dct["id"],
            dct["subreddit_id"],
            dct["num_comments"],
            dct["send_replies"],
            dct["whitelist_status"],
            dct["permalink"],
            dct["subreddit_subscribers"],
            RHF.unix_to_datetime(dct["created_utc"]),
            dct["num_crossposts"],
            [] if not "replies" in dct else [ReditComment.from_json(r) for r in dct["replies"]]
            )
