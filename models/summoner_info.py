class SummonerInfo:
    def summoner_info(self):
        if not self._summoner_info:
            endpoint = f"summoner/v4/summoners/by-name/{self.summoner_name}"
            self._summoner_info = self._get(endpoint)
        return self._summoner_info
    
    def summoner_id(self) -> str:
        return self.summoner_info()["id"]
    
    def summoner_puuid(self) -> str:
        return self.summoner_info()['puuid']
    
    def summoner_icon_id(self) -> int:
        return self.summoner_info()["profileIconId"]
    
    def summoner_level(self) -> int:
        return self.summoner_info()["summonerLevel"]