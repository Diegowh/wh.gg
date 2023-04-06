import requests
from typing import Dict, Any, Tuple
from time_stamp import SEASON_START_TIMESTAMP
from api_utils import make_request
import time


class Summoner:
    def __init__(self, api_key: str, region: str, summoner_name: str) -> None:
        self.api_key = api_key
        self.region = region
        self.summoner_name = summoner_name
        self.base_url = f"https://{region}.api.riotgames.com/lol/"
    
        
    def _get(self, endpoint, general_region=False, **params) -> Dict[str, Any] :
        '''Método privado para realizar una solicitud GET a la API de Riot utilizando el endpoint seleccionado.
        '''
        region_url = "europe" if general_region else self.region
        url = f"https://{region_url}.api.riotgames.com/lol/{endpoint}?api_key={self.api_key}"
        
        try:
            return make_request(url, params)
        except Exception as e:
            raise Exception(f"Error fetching data from API: {e}")
        
    def summoner_info(self):
        endpoint = f"summoner/v4/summoners/by-name/{self.summoner_name}"
        return self._get(endpoint)
    
    
    def summoner_id(self) -> str:
        return self.summoner_info()["id"]
    
    
    def summoner_puuid(self) -> str:
        return self.summoner_info()['puuid']
    
    
    def league_entries(self) -> Dict[str, Any]:
        endpoint = f"league/v4/entries/by-summoner/{self.summoner_id()}"
        return self._get(endpoint)
    
    
    def summoner_ranks(self)-> Dict[str, str]:
        '''Retorna el rank de soloq y flex en formato Dict'''
        league_entries = self.league_entries()
        ranks = {
            "soloq_rank": "Unranked", 
            "flex_rank": "Unranked",
            }
        
        for entry in league_entries:
            if entry["queueType"] == "RANKED_SOLO_5x5":
                ranks["soloq_rank"] = f"{entry['tier']} {entry['rank']}"
            elif entry["queueType"] == "RANKED_FLEX_SR":
                ranks["flex_rank"] = f"{entry['tier']} {entry['rank']}"
                
        return ranks
    
    
    def soloq_rank(self) -> str:
        return self.summoner_ranks()['soloq_rank']
    
    
    def flex_rank(self) -> str:
        return self.summoner_ranks()['flex_rank']
    
    
    def champions_data(self) -> Dict[str, Any]:
        endpoint = f"champion-mastery/v4/champion-masteries/by-summoner/{self.summoner_id()}"
        return self._get(endpoint) 
    
    
    def total_ranked_games_played(self) -> Tuple[int, int]:
        league_entries = self.league_entries()
        soloq_games_played = 0
        flex_games_played = 0
        
        for entry in league_entries:
            if entry["queueType"] == "RANKED_SOLO_5x5":
                soloq_games_played = entry["wins"] + entry["losses"]
            elif entry["queueType"] == "RANKED_FLEX_SR":
                flex_games_played = entry["wins"] + entry["losses"]
                
        return soloq_games_played, flex_games_played
    
    
    def all_ranked_matches_this_season(self) -> list:
        
        # start_time = time.time()
        
        soloq_games_played, flex_games_played = self.total_ranked_games_played()
        match_ids = []
        queue_game_played_pairs = [(420, soloq_games_played), (440, flex_games_played)]
        
        
        for queue, games_played in queue_game_played_pairs:
            for start_index in range(0, games_played, 100):
                endpoint = f"match/v5/matches/by-puuid/{self.summoner_puuid()}/ids"
                params = {
                    "startTime": int(SEASON_START_TIMESTAMP),
                    "queue": int(queue),
                    "start": int(start_index),
                    "count": int(min(100, games_played - start_index))
                }
                current_match_ids = self._get(endpoint, general_region=True, **params)
                match_ids += current_match_ids
                start_index += len(current_match_ids)
                
        # end_time = time.time()
        # execution_time = end_time - start_time
        # print(f"Execution time: {execution_time:.2f} seconds")

        return match_ids

    
    
    def games_data(self) -> dict:
        all_games_data = {}
        summoner_puuid = self.summoner_puuid()
        
        for match_id in self.all_ranked_matches_this_season():
            endpoint = f"match/v5/matches/{match_id}"
            match_request = self._get(general_region=True, endpoint=endpoint)
            
            # uno ambas listas con zip() para iterar sobre las dos a la vez
            for participant_puuid, participant_data in zip(match_request["metadata"]["participants"], match_request["info"]["participants"]):
                if participant_puuid == summoner_puuid:
                    match_data = {
                        "championName": participant_data["championName"],
                        "kills": participant_data["kills"],
                        "deaths": participant_data["deaths"],
                        "assists": participant_data["assists"],
                        "win": participant_data["win"],
                    }

                    all_games_data[match_id] = match_data
                    # como solo busco los datos de uno, meto break en el primer if
                    break
        
        return all_games_data


    def champion_stats(self) -> dict[str, dict]:
        
        champion_stats = {}
        games_data = self.games_data()
        for game_data in games_data.values():
            champion = game_data["championName"]
            # compruebo si ya hay datos de ese champ
            if champion not in champion_stats:
                champion_stats[champion] = {
                    "kills": 0,
                    "deaths": 0,
                    "assists": 0,
                    "wins": 0,
                    "games_played": 0
                }
            
            champion_stats[champion]["kills"] += game_data["kills"]
            champion_stats[champion]["deaths"] += game_data["deaths"]
            champion_stats[champion]["assists"] += game_data["assists"]
            champion_stats[champion]["wins"] += int(game_data["win"]) # al pasar bool a int, True = 1, False = 0.
            champion_stats[champion]["games_played"] += 1

        # calculo el winratio y KDA, etc.
        for champion in champion_stats:
            
            champion_stats[champion]["win_ratio"] = int(round((champion_stats[champion]["wins"] / champion_stats[champion]["games_played"]) * 100))
            
            champion_stats[champion]["kda"] = round(((champion_stats[champion]["kills"] + champion_stats[champion]["assists"]) / champion_stats[champion]["deaths"]), 2)
            
            champion_stats[champion]["avg_kills"] = round((champion_stats[champion]["kills"] / champion_stats[champion]["games_played"]), 1)
            
            champion_stats[champion]["avg_deaths"] = round((champion_stats[champion]["deaths"] / champion_stats[champion]["games_played"]), 1)
            
            champion_stats[champion]["avg_assists"] = round((champion_stats[champion]["assists"] / champion_stats[champion]["games_played"]), 1)
    
        
        return champion_stats
    
    
