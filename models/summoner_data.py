import sqlite3
from .database_handler import DatabaseHandler
from .summoner_info import SummonerInfo
from .api_handler import APIHandler
from .ranked_data import RankedData
from .match_stats import MatchStats


class SummonerData(SummonerInfo, DatabaseHandler, APIHandler, RankedData, MatchStats):
    def __init__(self, summoner_name: str, api_key: str, region: str = "EUW1") -> None:
        self.api_key = api_key
        self.region = region
        self.summoner_name = summoner_name
        self.base_url = f"https://{region}.api.riotgames.com/lol/"
        
        self._summoner_info = None
        self.id = self.summoner_id()
        self.db = sqlite3.connect("data.db")
        
        # self.cache = cachetools.TTLCache(maxsize=100, ttl=30 * 60)
        
        if self._summoner_data_from_db() is not None:
            self.puuid = self._summoner_data_from_db()["summoner_puuid"]
            self.icon_id = self._summoner_data_from_db()["profile_icon_id"]
            self.level = self._summoner_data_from_db()["summoner_level"]
        else:
            self.puuid = self.summoner_puuid()
            self.icon_id = self.summoner_icon_id()
            self.level = self.summoner_level()