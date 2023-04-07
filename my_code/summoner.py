from typing import Dict, Any, Tuple
from season_constants import SEASON_START_TIMESTAMP
from request_utils import make_request
import cachetools



class Summoner:
    def __init__(self, api_key: str, region: str, summoner_name: str) -> None:
        self.api_key = api_key
        self.region = region
        self.summoner_name = summoner_name
        self.base_url = f"https://{region}.api.riotgames.com/lol/"
        self._summoner_info = None
        #TODO Crear un sistema de almacenamiento en cache externo a Summoner que se almacene en una base de datos.
        self.cache = cachetools.TTLCache(maxsize=100, ttl=30 * 60) # cache con un maximo de 100 elementos y un tiempo de vida de media hora (30 minutos * 60 segundos)
        self.puuid = self.summoner_puuid()
        self.id = self.summoner_id()
    
        
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
        if not self._summoner_info:
            endpoint = f"summoner/v4/summoners/by-name/{self.summoner_name}"
            self._summoner_info = self._get(endpoint)
        return self._summoner_info
    
    
    def summoner_id(self) -> str:
        return self.summoner_info()["id"]
    
    
    def summoner_puuid(self) -> str:
        return self.summoner_info()['puuid']
    
    
    def league_entries(self) -> Dict[str, Any]:
        endpoint = f"league/v4/entries/by-summoner/{self.id}"
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
        endpoint = f"champion-mastery/v4/champion-masteries/by-summoner/{self.id}"
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
                endpoint = f"match/v5/matches/by-puuid/{self.puuid}/ids"
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
        """Comprueba si los datos para dadao summoner_puuid ya estan en cache antes de ejecutar la funcion _games_data(). Si existen los devuelve de la cache sin ejecutar la funcion siguiente. En el caso de que no existan, ejecuta _games_data
        """
        
        cache_key = f"{self.puuid}_games_data"
        
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        all_games_data = self._games_data()
        self.cache[cache_key] = all_games_data
        print(f"Data stored in cache for key {cache_key}")
        return all_games_data
        
        
    def _games_data(self) -> dict:    
        """Tomando los match ID de las rankeds jugadas en toda la temporada, devuelve los datos del usuario en estas partidas.

        Returns:
            dict: Champion name, kills, deaths, assists, win
        """
        
        all_games_data = {}
        
        for match_id in self.all_ranked_matches_this_season():
            endpoint = f"match/v5/matches/{match_id}"
            match_request = self._get(general_region=True, endpoint=endpoint)
            
            participants = {
                participant["puuid"]: participant
                for participant in match_request["info"]["participants"]
            }
            
            if self.puuid in participants:
                participant_data = participants[self.puuid]
                match_data = {
                    "championName": participant_data["championName"],
                    "kills": participant_data["kills"],
                    "deaths": participant_data["deaths"],
                    "assists": participant_data["assists"],
                    "win": participant_data["win"],
                }

                all_games_data[match_id] = match_data

        
        return all_games_data


    # funciones auxiliares para evitar codigo redundante
    def calculate_kda(self, kills: int, deaths: int, assists: int) -> float:
        kda = (kills + assists) / (deaths if deaths != 0 else 1)
        return round(kda, 2)


    def calculate_average(self, value: int, total_games: int) -> float:
        return round(value / total_games, 1)
    
    
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
            
            champion_stats[champion]["kda"] = self.calculate_kda(champion_stats[champion]["kills"], champion_stats[champion]["deaths"], champion_stats[champion]["assists"])
            
            champion_stats[champion]["avg_kills"] = self.calculate_average(champion_stats[champion]["kills"], champion_stats[champion]["games_played"])
            
            champion_stats[champion]["avg_deaths"] = self.calculate_average(champion_stats[champion]["deaths"], champion_stats[champion]["games_played"])
            
            champion_stats[champion]["avg_assists"] = self.calculate_average(champion_stats[champion]["assists"], champion_stats[champion]["games_played"])
    
        
        return champion_stats
    
    
    
    def recent_10_games_data(self) -> list[dict]:
        recent_10_games = []
        all_ranked_matches = self.all_ranked_matches_this_season()
        # TODO Optimizar esto para no tener que sacar todas las partidas de una season. Crear otro metodo que sea especifico para las ultimas 10 partidas.
        
        # por cada id de partida hago solicitud para obtener sus datos
        for match_id in reversed(all_ranked_matches[-10:]):
            endpoint = f"match/v5/matches/{match_id}"
            match_request = self._get(general_region=True, endpoint=endpoint)
            
            blue_team = []
            red_team = []
            
            # summoner name y champion de cada jugador (separado por blue o red team)
            for participant_data in match_request["info"]["participants"]:
                participant_info = {
                    "summoner_name": participant_data["summonerName"],
                    "champion_name": participant_data["championName"]
                }
                if participant_data["teamId"] == 100:
                    blue_team.append(participant_info)
                else:
                    red_team.append(participant_info)
                    
                
                if participant_data["puuid"] == self.puuid:
                    game_data = {
                        "game_mode": match_request["info"]["gameMode"],
                        "win": participant_data["win"],
                        "champion_name": participant_data["championName"], #TODO A lo mejor puedo quitar esto ya que esta en la lista de arriba
                        "score": f'{participant_data["kills"]}/{participant_data["deaths"]}/{participant_data["assists"]}',
                        "kda": self.calculate_kda(participant_data["kills"], participant_data["deaths"], participant_data["assists"]),
                        "cs": participant_data["totalMinionsKilled"] + participant_data["neutralMinionsKilled"],
                        "vision_score": participant_data["visionScore"],
                        "build": [
                            participant_data["item0"], 
                            participant_data["item1"], 
                            participant_data["item2"], 
                            participant_data["item3"], 
                            participant_data["item4"], 
                            participant_data["item5"], 
                            participant_data["item6"]
                            ],
                    }
            
            game_data["blue_team"] = blue_team
            game_data["red_team"] = red_team
            recent_10_games.append(game_data)
            
        return recent_10_games
    
    
    