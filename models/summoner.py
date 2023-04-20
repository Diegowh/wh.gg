from typing import Dict, Any, Tuple
from utils.season_constants import SEASON_START_TIMESTAMP
from utils.request_utils import make_request
import cachetools
import sqlite3
import time
import roman

HOUR = 3600
RECENT_MATCHES_LIMIT = 10

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
        
        if self.summoner_data_from_db() is not None:
            self.puuid = self.summoner_data_from_db()["summoner_puuid"]
            self.icon_id = self.summoner_data_from_db()["profile_icon_id"]
            self.level = self.summoner_data_from_db()["summoner_level"]
        else:
            self.puuid = self.summoner_puuid()
            self.icon_id = self.summoner_icon_id()
            self.level = self.summoner_level()
        
        
    def summoner_data_from_db(self) -> dict:
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT summoner_puuid, profile_icon_id, summoner_level FROM summoners WHERE summoner_name = ?",
                (self.summoner_name,),
            )
            result = cursor.fetchone()
            
            if result is not None:
                data = {
                    "summoner_puuid": result[0],
                    "profile_icon_id": result[1],
                    "summoner_level": result[2],
                }
                return data
            else:
                return None
    
    
    def save_or_update_summoner_to_db(self, league_data: dict) -> None:
        '''
        Guarda o actualiza los datos del summoner, dependiendo de si existia una ultima actualizacion o no.
        '''
        with self.db as conn:
            cursor = conn.cursor()
            current_timestamp = int(time.time())
            
            # busco la ultima actualizacion de los datos de ese puuid
            cursor.execute("SELECT last_update FROM summoners WHERE summoner_puuid = ?", (self.puuid,))
            result = cursor.fetchone()
            
            if result:
                last_update = result[0]
                if current_timestamp - last_update >= HOUR: # una hora
                    print("Updating summoner data in the database.")
                    cursor.execute(
                        """
                        UPDATE summoners SET
                        summoner_id = ?, summoner_name = ?, region = ?, last_update = ?,
                        soloq_rank = ?, soloq_lp = ?, soloq_wins = ?, soloq_losses = ?, soloq_wr = ?,
                        flex_rank = ?, flex_lp = ?, flex_wins = ?, flex_losses = ?, flex_wr = ?, profile_icon_id = ?, summoner_level = ?
                        WHERE summoner_puuid = ?
                        """,
                        (self.id, self.summoner_name, self.region, current_timestamp,
                        league_data["soloq_rank"], league_data["soloq_lp"], league_data["soloq_wins"], league_data["soloq_losses"], league_data["soloq_wr"],
                        league_data["flex_rank"], league_data["flex_lp"], league_data["flex_wins"], league_data["flex_losses"], league_data["flex_wr"], self.icon_id, self.level,
                        self.puuid)
                    )
                else:
                    print("Summoner data is up-to-date.")
                    
            else:
                cursor.execute(
                    "INSERT INTO summoners (summoner_puuid, summoner_id, summoner_name, region, last_update, soloq_rank, soloq_lp, soloq_wins, soloq_losses, soloq_wr, flex_rank, flex_lp, flex_wins, flex_losses, flex_wr, profile_icon_id, summoner_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (self.puuid, self.id, self.summoner_name, self.region, current_timestamp, league_data["soloq_rank"], league_data["soloq_lp"], league_data["soloq_wins"], league_data["soloq_losses"], league_data["soloq_wr"],league_data["flex_rank"],league_data["flex_lp"],league_data["flex_wins"],league_data["flex_losses"],league_data["flex_wr"], self.icon_id, self.level),
                )
            conn.commit()
        
        
    def _summoner_data_from_db(self) -> dict:
        '''
        Devuelve un diccionario con los datos de un summoner almacenados en la base de datos
        '''
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT soloq_rank, soloq_lp, soloq_wins, soloq_losses, soloq_wr, 
                flex_rank, flex_lp, flex_wins, flex_losses, flex_wr, profile_icon_id, summoner_level
                FROM summoners WHERE summoner_puuid = ?
                """,
                (self.puuid,)
            )
            result = cursor.fetchone()
            
            if result:
                summoner_data = {
                    "soloq_rank": result[0],
                    "soloq_lp": result[1],
                    "soloq_wins": result[2],
                    "soloq_losses": result[3],
                    "soloq_wr": result[4],
                    "flex_rank": result[5],
                    "flex_lp": result[6],
                    "flex_wins": result[7],
                    "flex_losses": result[8],
                    "flex_wr": result[9],
                    "profile_icon_id": result[10],
                    "summoner_level": result[11],
                }
                return summoner_data

            else:
                return None
        
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
    
    
    def summoner_icon_id(self) -> int:
        return self.summoner_info()["profileIconId"]
    
    
    def summoner_level(self) -> int:
        return self.summoner_info()["summonerLevel"]
    
    
    def league_entries(self) -> Dict[str, Any]:
        endpoint = f"league/v4/entries/by-summoner/{self.id}"
        return self._get(endpoint)
    
    
    def fetch_summoner_ranks(self)-> Dict[str, str]:
        '''Retorna el rank de soloq y flex en formato Dict'''
        league_entries = self.league_entries()
        ranks = {
            "soloq_rank": "Unranked",
            "soloq_lp": 0,
            "soloq_wins": 0,
            "soloq_losses": 0,
            "soloq_wr": 0,
            "flex_rank": "Unranked",
            "flex_lp": 0,
            "flex_wins": 0,
            "flex_losses": 0,
            "flex_wr": 0,
            "profile_icon_id": self.summoner_icon_id(),
            "summoner_level": self.summoner_level(),
        }
        
        # Itero sobre las 2 entradas (soloq y flex) porque los retrasados de riot las devuelven en orden aleatorio en cada solicitud
        for entry in league_entries:
            win_rate = int(round((entry['wins'] / (entry['wins'] + entry['losses'])) * 100))
            if entry["queueType"] == "RANKED_SOLO_5x5":
                ranks["soloq_rank"] = f"{entry['tier']} {roman.fromRoman(entry['rank'])}"
                ranks["soloq_lp"] = entry['leaguePoints']
                ranks["soloq_wins"] = entry['wins']
                ranks["soloq_losses"] = entry['losses']
                ranks["soloq_wr"] = win_rate
            elif entry["queueType"] == "RANKED_FLEX_SR":
                ranks["flex_rank"] = f"{entry['tier']} {roman.fromRoman(entry['rank'])}"
                ranks["flex_lp"] = entry['leaguePoints']
                ranks["flex_wins"] = entry['wins']
                ranks["flex_losses"] = entry['losses']
                ranks["flex_wr"] = win_rate

        return ranks
    
    
    def soloq_rank(self) -> str:
        return self.fetch_summoner_ranks()['soloq_rank']
    
    
    def flex_rank(self) -> str:
        return self.fetch_summoner_ranks()['flex_rank']
    
    
    def league_data(self) -> dict:
        '''
        Intenta obtener los datos de soloq y flex desde la base de datos. Si no existen, los solicita a la API con fetch_summoner_ranks() y los guarda en la base de datos.
        Además, si han pasado más de una hora desde la última actualización, actualiza los datos de partidas y la información del invocador en la base de datos.
        '''
        
        summoner_data = self._summoner_data_from_db()
        
        if summoner_data:
            return summoner_data
        else:
            
            data = self.fetch_summoner_ranks()
            self.save_or_update_summoner_to_db(data)
            
            return data
    
    
    def total_ranked_games_played_per_queue(self) -> tuple:
        league_entries = self.league_entries()
        soloq_games_played = 0
        flex_games_played = 0

        for entry in league_entries:
            if entry["queueType"] == "RANKED_SOLO_5x5":
                soloq_games_played = entry["wins"] + entry["losses"]
            elif entry["queueType"] == "RANKED_FLEX_SR":
                flex_games_played = entry["wins"] + entry["losses"]

        return (soloq_games_played, flex_games_played)
    
    
    # TODO  Revisar CHAMPION_STATS porque ahora esta teniendo en cuenta todos los match_ids, si quiero que sea de ranked hay que incluir una condicion para filtrar match ids.
    def all_match_ids_this_season(self) -> list:
        '''
        Devuelve todos los match id de las partidas jugadas.
        '''
        MAX_GAMES = 5000
        match_ids = []
        
        for start_index in range(0, MAX_GAMES, 100):
            endpoint = f"match/v5/matches/by-puuid/{self.puuid}/ids"
            params = {
                "startTime": SEASON_START_TIMESTAMP,
                "start": start_index,
                "count": int(min(100, MAX_GAMES - start_index))
            }
            current_match_ids = self._get(endpoint, general_region=True, **params)
            
            if not current_match_ids:
                break
            
            match_ids += current_match_ids
            
        return match_ids
    
    def recent_matches_data(self) -> list:
        matches_data = self._matches_data_from_db()
        self.update_champion_stats()

        def match_id_key(match_data):
            return match_data["match_id"]

        matches_data.sort(key=match_id_key, reverse=True)
        recent_matches_data = matches_data[:RECENT_MATCHES_LIMIT]

        return recent_matches_data

    
    
    def _matches_data_from_db(self) -> list[dict]:
        with self.db as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT match_id FROM matches WHERE summoner_puuid = ? ORDER BY match_id DESC LIMIT 1",
                (self.puuid,)
            )
            last_match_id =  cursor.fetchone()
            
            if last_match_id:
                recent_matches = [
                    match_id for match_id in self.all_match_ids_this_season() if match_id > last_match_id[0]
                ]
                if recent_matches:
                    new_matches_data = self._matches_data(recent_matches)
                    self.save_matches_data_to_db(new_matches_data)
            
            else:
                all_matches = self.all_match_ids_this_season()
                if all_matches:
                    all_matches_data = self._matches_data(all_matches)
                    self.save_matches_data_to_db(all_matches_data)
            
            cursor.execute(
                "SELECT * FROM matches WHERE summoner_puuid = ?", (self.puuid,)
            )
            result = cursor.fetchall()
            matches_data = []
            for row in result:
                match_data = {
                    "summoner_puuid": row[1],
                    "match_id": row[2],
                    "champion_name": row[3],
                    "win": row[4],
                    "kills": row[5],
                    "deaths": row[6],
                    "assists": row[7],
                    "kda": row[8],
                    "cs": row[9],
                    "vision": row[10],
                    "summoner_spell1": row[11],
                    "summoner_spell2": row[12],
                    "item0": row[13],
                    "item1": row[14],
                    "item2": row[15],
                    "item3": row[16],
                    "item4": row[17],
                    "item5": row[18],
                    "item6": row[19],
                    "participant1_summoner_name": row[20],
                    "participant2_summoner_name": row[21],
                    "participant3_summoner_name": row[22],
                    "participant4_summoner_name": row[23],
                    "participant5_summoner_name": row[24],
                    "participant6_summoner_name": row[25],
                    "participant7_summoner_name": row[26],
                    "participant8_summoner_name": row[27],
                    "participant9_summoner_name": row[28],
                    "participant10_summoner_name": row[29],
                    "participant1_champion_name": row[30],
                    "participant2_champion_name": row[31],
                    "participant3_champion_name": row[32],
                    "participant4_champion_name": row[33],
                    "participant5_champion_name": row[34],
                    "participant6_champion_name": row[35],
                    "participant7_champion_name": row[36],
                    "participant8_champion_name": row[37],
                    "participant9_champion_name": row[38],
                    "participant10_champion_name": row[39],
                    "participant1_team_id": row[40],
                    "participant2_team_id": row[41],
                    "participant3_team_id": row[42],
                    "participant4_team_id": row[43],
                    "participant5_team_id": row[44],
                    "participant6_team_id": row[45],
                    "participant7_team_id": row[46],
                    "participant8_team_id": row[47],
                    "participant9_team_id": row[48],
                    "participant10_team_id": row[49],
                    "game_mode": row[50],
                    "game_duration": row[51],
                    "queue_id": row[52],
                }
                matches_data.append(match_data)
                
        return matches_data
    
    
    def save_matches_data_to_db(self, matches_data: dict) -> None:
        with self.db as conn:
            cursor = conn.cursor()

            for match_id, game_data in matches_data.items():
                match_data = game_data["match_data"]
                summoner_data = game_data["summoner_data"]
                participants_data = game_data["participants_data"]
                
                cursor.execute(
                    """
                    INSERT INTO matches (
                        summoner_puuid, match_id, champion_name, win, kills, deaths, assists, kda, cs, vision, 
                        summoner_spell1, summoner_spell2, item0, item1, item2, item3, item4, item5, item6,
                        participant1_summoner_name, participant2_summoner_name, participant3_summoner_name, participant4_summoner_name, participant5_summoner_name, 
                        participant6_summoner_name, participant7_summoner_name, participant8_summoner_name, participant9_summoner_name, participant10_summoner_name, 
                        participant1_champion_name, participant2_champion_name, participant3_champion_name, participant4_champion_name, participant5_champion_name, 
                        participant6_champion_name, participant7_champion_name, participant8_champion_name, participant9_champion_name, participant10_champion_name, 
                        participant1_team_id, participant2_team_id, participant3_team_id, participant4_team_id, participant5_team_id, 
                        participant6_team_id, participant7_team_id, participant8_team_id, participant9_team_id, participant10_team_id, game_mode, game_duration, queue_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        summoner_data["summoner_puuid"],
                        match_id,
                        summoner_data["champion_name"],
                        summoner_data["win"],
                        summoner_data["kills"],
                        summoner_data["deaths"],
                        summoner_data["assists"],
                        summoner_data["kda"],
                        summoner_data["cs"],
                        summoner_data["vision"],
                        summoner_data["summoner_spell1"],
                        summoner_data["summoner_spell2"],
                        summoner_data["item0"],
                        summoner_data["item1"],
                        summoner_data["item2"],
                        summoner_data["item3"],
                        summoner_data["item4"],
                        summoner_data["item5"],
                        summoner_data["item6"],
                        participants_data[0]["summoner_name"],
                        participants_data[1]["summoner_name"],
                        participants_data[2]["summoner_name"],
                        participants_data[3]["summoner_name"],
                        participants_data[4]["summoner_name"],
                        participants_data[5]["summoner_name"],
                        participants_data[6]["summoner_name"],
                        participants_data[7]["summoner_name"],
                        participants_data[8]["summoner_name"],
                        participants_data[9]["summoner_name"],
                        participants_data[0]["champion_name"],
                        participants_data[1]["champion_name"],
                        participants_data[2]["champion_name"],
                        participants_data[3]["champion_name"],
                        participants_data[4]["champion_name"],
                        participants_data[5]["champion_name"],
                        participants_data[6]["champion_name"],
                        participants_data[7]["champion_name"],
                        participants_data[8]["champion_name"],
                        participants_data[9]["champion_name"],
                        participants_data[0]["team_id"],
                        participants_data[1]["team_id"],
                        participants_data[2]["team_id"],
                        participants_data[3]["team_id"],
                        participants_data[4]["team_id"],
                        participants_data[5]["team_id"],
                        participants_data[6]["team_id"],
                        participants_data[7]["team_id"],
                        participants_data[8]["team_id"],
                        participants_data[9]["team_id"],
                        match_data["game_mode"],
                        match_data["game_duration"],
                        match_data["queue_id"]
                    ),
            )
        conn.commit()

        
    def _matches_data(self, match_ids: list = None) -> dict:    
        """
        Devuelve un diccionario con los datos del summoner y los datos de todos los participantes para cada match_id.
        """
        if match_ids is None:
            match_ids = self.all_match_ids_this_season()
            
        all_matches_data = {}
        
        for match_id in match_ids:
            endpoint = f"match/v5/matches/{match_id}"
            match_request = self._get(general_region=True, endpoint=endpoint)
            
            summoner_data = None
            participants_data = []


            for participant in match_request["info"]["participants"]:
                participant_info = {
                    "summoner_name": participant["summonerName"],
                    "champion_name": participant["championName"],
                    "team_id": participant["teamId"],
                }
                participants_data.append(participant_info)
                
                if participant["puuid"] == self.puuid:
                    summoner_data = {
                        "summoner_puuid": self.puuid,
                        "champion_name": participant["championName"],
                        "kills": participant["kills"],
                        "deaths": participant["deaths"],
                        "assists": participant["assists"],
                        "win": participant["win"],
                        "kda": self.calculate_kda(participant["kills"], participant["deaths"], participant["assists"]),
                        "cs": participant["totalMinionsKilled"] + participant["neutralMinionsKilled"],
                        "vision": participant["visionScore"],
                        "summoner_spell1": participant["summoner1Id"],
                        "summoner_spell2": participant["summoner2Id"],
                        "item0": participant["item0"],
                        "item1": participant["item1"],
                        "item2": participant["item2"],
                        "item3": participant["item3"],
                        "item4": participant["item4"],
                        "item5": participant["item5"],
                        "item6": participant["item6"],
                        
                    }
            match_data = {
                "game_mode": match_request["info"]["gameMode"],
                "game_duration": match_request["info"]["gameDuration"],
                "queue_id": match_request["info"]["queueId"]
            }
            all_match_data= {
                "match_data": match_data,
                "summoner_data": summoner_data,
                "participants_data": participants_data,
            }
            all_matches_data[match_id] = all_match_data
        
        return all_matches_data

    # funciones auxiliares para evitar codigo redundante
    def calculate_kda(self, kills: int, deaths: int, assists: int) -> float:
        kda = (kills + assists) / (deaths if deaths != 0 else 1)
        return round(kda, 2)


    def calculate_average(self, value: int, total_games: int) -> float:
        return round(value / total_games, 1)
    

    def update_champion_stats(self):
        with self.db as conn:
            cursor = conn.cursor()

            # Crea una tabla temporal con los datos agregados de matches
            cursor.execute(
                """
                CREATE TEMPORARY TABLE temp_stats AS
                SELECT
                    m.summoner_puuid,
                    m.champion_name,
                    COUNT(*) as matches_played,
                    SUM(m.win) as wins,
                    COUNT(*) - SUM(m.win) as losses,
                    ROUND(SUM(m.win) * 100.0 / COUNT(*)) as wr,
                    ROUND((SUM(m.kills) + SUM(m.assists)) / (SUM(m.deaths) + 0.001), 2) as kda,
                    ROUND(SUM(m.kills) * 1.0 / COUNT(*), 1) as kills,
                    ROUND(SUM(m.deaths) * 1.0 / COUNT(*), 1) as deaths,
                    ROUND(SUM(m.assists) * 1.0 / COUNT(*), 1) as assists,
                    ROUND(SUM(m.cs) * 1.0 / COUNT(*)) as cs
                FROM matches m
                WHERE (m.queue_id = '420' OR m.queue_id = '440')
                GROUP BY m.summoner_puuid, m.champion_name;
                """
            )

            # Insertar los registros de la tabla temporal en champion_stats
            cursor.execute(
                """
                INSERT INTO champion_stats
                (summoner_puuid, champion_name, matches_played, wins, losses, wr, kda, kills, deaths, assists, cs)
                SELECT
                    summoner_puuid,
                    champion_name,
                    matches_played,
                    wins,
                    losses,
                    wr,
                    kda,
                    kills,
                    deaths,
                    assists,
                    cs
                FROM temp_stats
                WHERE NOT EXISTS (
                    SELECT 1 FROM champion_stats
                    WHERE champion_stats.summoner_puuid = temp_stats.summoner_puuid AND champion_stats.champion_name = temp_stats.champion_name
                );
                """
            )
    
    def top_champions_data(self, top=5):
        
        with self.db as conn:
            cursor = conn.cursor()

            cursor.execute(f"""
                SELECT champion_name, matches_played, wr, kda, kills, deaths, assists, cs 
                FROM champion_stats
                WHERE summoner_puuid = '{self.puuid}'
                ORDER BY matches_played DESC, wr DESC, kda DESC
                LIMIT {top}
                """
                )

            top_champions_list = cursor.fetchall()
            
            top_champions = []
            for champion in top_champions_list:
                champion_dict = {}
                champion_dict["champion_name"] = champion[0]
                champion_dict["matches_played"] = champion[1]
                champion_dict["wr"] = champion[2]
                champion_dict["kda"] = champion[3]
                champion_dict["kills"] = champion[4]
                champion_dict["deaths"] = champion[5]
                champion_dict["assists"] = champion[6]
                champion_dict["cs"] = champion[7]
                top_champions.append(champion_dict)
            
            return top_champions
        
        
# TODO Hay un error conocido que incluye los datos de todas las partidas jugadas en modo CLASSIC (normal, soloq, flex) en champions_data.
    
# TODO: Code Smells and Improvements:

"""
1. Long class: The Summoner class is quite long, with many methods for fetching and processing data. Consider breaking the class into smaller classes, each with a specific responsibility (e.g., one class for database handling, another for API requests, and a third for data processing).

2. Multiple languages: The code comments and print statements are in different languages. Ensure that comments and output are consistent, ideally in English for broader accessibility.

3. Repeated code: Several methods contain repeated code patterns, such as cursor initialization and database query execution. Consider creating a separate method to handle these repetitive tasks to improve code readability and reduce duplication.

4. Magic numbers: There are a few hardcoded numbers in the code, such as time intervals and cache sizes. Replace these magic numbers with named constants for better readability and maintainability.

5. Use context managers: When working with databases, it's better to use context managers (i.e., with statement) to ensure that resources like cursors are properly closed.

6. Replace __del__ with a context manager: The __del__ method is not guaranteed to be called when an object is garbage collected. Instead, implement a context manager using __enter__ and __exit__ methods to handle resource clean-up (e.g., closing the database connection).

7. Error handling: The _get method raises a generic Exception. Consider raising a more specific exception or using a custom exception class to provide better error information.

8. Avoid storing the API key in the class: Storing sensitive information like the API key in the class can be a security risk. Pass the API key as an argument to the methods that require it, or use environment variables or configuration files to store sensitive information.

9. Inline comments: Some inline comments are lengthy and could be better placed above the code line they are describing. This will improve code readability.

10. Remove unnecessary conversion to int in dictionary: In the all_ranked_matches_this_season method, start and count are already integers, so there is no need to wrap them with int().

11. Method and variable naming: Some method and variable names are not descriptive enough, making it harder to understand their purpose. Consider using more descriptive names for better code readability (e.g., soloq_rank could be solo_queue_rank)."""