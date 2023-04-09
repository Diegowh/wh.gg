from typing import Dict, Any, Tuple
from season_constants import SEASON_START_TIMESTAMP
from request_utils import make_request
import cachetools
import sqlite3


class Summoner:
    def __init__(self, summoner_name: str, api_key: str, region: str = "EUW1") -> None:
        self.api_key = api_key
        self.region = region
        self.summoner_name = summoner_name
        self.base_url = f"https://{region}.api.riotgames.com/lol/"
        
        self._summoner_info = None
        self.cache = cachetools.TTLCache(maxsize=100, ttl=30 * 60) # cache con un maximo de 100 elementos y un tiempo de vida de media hora (30 minutos * 60 segundos)
        self.id = self.summoner_id()
        
        self.db = sqlite3.connect("data.db")
        self.puuid = self.summoner_puuid_from_db()
        if self.puuid is None:
            self.puuid = self.summoner_puuid()
            self.save_summoner_to_db()
            
            
    def __del__(self):
        self.db.close()
        
        
    def summoner_puuid_from_db(self) -> str:
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT summoner_puuid FROM summoners WHERE summoner_name = ?",
            (self.summoner_name,),
        )
        result = cursor.fetchone()
        return result[0] if result is not None else None
    
    
    def save_summoner_to_db(self) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO summoners (summoner_puuid, summoner_id, summoner_name, region) VALUES (?, ?, ?, ?)",
            (self.puuid, self.summoner_id(), self.summoner_name, self.region),
        )
        self.db.commit()
        
        
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
    
    
    def total_ranked_games_played_per_queue(self) -> Tuple[int, int]:
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
        '''
        Devuelve todos los match id de las partidas jugadas.
        '''
        soloq_games_played, flex_games_played = self.total_ranked_games_played_per_queue()
        games_played = sum([soloq_games_played, flex_games_played])
        
        match_ids = []
        
        for start_index in range(0, games_played, 100):
            endpoint = f"match/v5/matches/by-puuid/{self.puuid}/ids"
            params = {
                "startTime": int(SEASON_START_TIMESTAMP),
                "start": int(start_index),
                "count": int(min(100, games_played - start_index))
            }
            current_match_ids = self._get(endpoint, general_region=True, **params)
            match_ids += current_match_ids

        return match_ids

    
    
    def games_data(self) -> dict:
        games_data = self.games_data_from_db()
        if not games_data:
            games_data = self._games_data()
            self.save_games_data_to_db(games_data)
        return games_data
    
    
    def games_data_from_db(self) -> dict:
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM Matches WHERE summoner_puuid = ?", (self.puuid,)
        )
        result = cursor.fetchall()
        games_data = {}
        for row in result:
            match_id = row[0]
            game_data = {
            "championName": row[2],
            "kills": row[3],
            "deaths": row[4],
            "assists": row[5],
            "win": row[6]
        }
            games_data[match_id] = game_data
            
        return games_data
    
    
    def save_games_data_to_db(self, games_data: dict) -> None:
        cursor = self.db.cursor()
        
        for match_id, game_data in games_data.items():
            cursor.execute(
                "INSERT INTO Matches (match_id, summoner_puuid, champion_name, kills, deaths, assists, win) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    match_id,
                    self.puuid,
                    game_data["championName"],
                    game_data["kills"],
                    game_data["deaths"],
                    game_data["assists"],
                    game_data["win"],
                ),
            )
        self.db.commit()
        
        
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
    
    
    def champion_stats(self):
        champion_stats = {}
        games_data = self.games_data()
        for game_data in games_data.values():
            champion = game_data["championName"]
            stats = champion_stats.setdefault(champion, {"kills": 0, "deaths": 0, "assists": 0, "wins": 0, "games_played": 0})
            stats["kills"] += game_data["kills"]
            stats["deaths"] += game_data["deaths"]
            stats["assists"] += game_data["assists"]
            stats["wins"] += int(game_data["win"])
            stats["games_played"] += 1

        for stats in champion_stats.values():
            stats["win_ratio"] = int(round((stats["wins"] / stats["games_played"]) * 100))
            stats["kda"] = self.calculate_kda(stats["kills"], stats["deaths"], stats["assists"])
            stats["avg_kills"] = self.calculate_average(stats["kills"], stats["games_played"])
            stats["avg_deaths"] = self.calculate_average(stats["deaths"], stats["games_played"])
            stats["avg_assists"] = self.calculate_average(stats["assists"], stats["games_played"])

        return champion_stats
    
    
    
    def top_champs_played(self, champion_stats, top=5):
        
        sorted_champs = sorted(champion_stats.items(), key=lambda x: x[1]['games_played'], reverse=True)
        return sorted_champs[:top]
    
    
    
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
    
    
    def get_new_matches(self) -> list:
        '''
        Compara los match_id de la base de datos con los obtenidos de la ultima solicitud a la API y devuelve una lista de los que no se encuentren en la abse de datos.
        '''
        all_matches = self.all_ranked_matches_this_season()
        db_matches = self.match_ids_from_db()
        new_matches = [match for match in all_matches if match not in db_matches]
        
        return new_matches
    
    
    def match_ids_from_db(self):
        '''
        Devuelve los match id de la base de datos.
        '''
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT match_id FROM Matches WHERE summoner_puuid = ?", (self.puuid,)
        )
        result = cursor.fetchall()
        match_ids = [row[0] for row in result]
        return match_ids