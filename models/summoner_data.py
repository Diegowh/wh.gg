from typing import Dict, Any
from utils.season_constants import SEASON_START_TIMESTAMP
from utils.request_utils import make_request
# import cachetools
import sqlite3
import time
import roman
from sqlalchemy.orm import Session
from .db_models import db, SummonerModel, ChampionStatsModel, MatchModel

UPDATE_THRESHOLD = 3600
RECENT_MATCHES_LIMIT = 10

class SummonerData:
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
        
        
    def _summoner_data_from_db(self) -> dict:
        """Retrieve summoner data from the database based on the summoner_name.
        Returns:
            A dict with summoner data or None if not found.
        """
        
        summoner_model = SummonerModel.query.filter_by(summoner_name=self.summoner_name).first()
        return {
                "summoner_puuid": summoner_model.summoner_puuid,
                "profile_icon_id": summoner_model.profile_icon_id,
                "summoner_level": summoner_model.summoner_level,
                "soloq_rank": summoner_model.soloq_rank,
                "soloq_lp": summoner_model.soloq_lp,
                "soloq_wins": summoner_model.soloq_wins,
                "soloq_losses": summoner_model.soloq_losses,
                "soloq_wr": summoner_model.soloq_wr,
                "flex_rank": summoner_model.flex_rank,
                "flex_lp": summoner_model.flex_lp,
                "flex_wins": summoner_model.flex_wins,
                "flex_losses": summoner_model.flex_losses,
                "flex_wr": summoner_model.flex_wr,
            } if summoner_model else None
    
    
    def save_or_update_summoner_to_db(self, league_data: dict) -> None:
        """Saves or updates summoner data to the database based on whether the summoner's data has been updated within the last update time threshold (1 hour) or not.
        
        Args:
            league_data: A dict containing the summoner's ranked and profile information.
            session: a SQLAlchemy database session.
            
            Returns:
                None
        """

        current_timestamp = int(time.time())
        
        # Check if the summoner exists in the database
        summoner_model = SummonerModel.query.filter_by(summoner_puuid=self.puuid).first()
        
        if summoner_model:
            last_update = summoner_model.last_update
            
            if current_timestamp - last_update >= UPDATE_THRESHOLD:
                print("Updating database...")

                summoner_model.summoner_id = self.id
                summoner_model.summoner_name = self.summoner_name
                summoner_model.region = self.region
                summoner_model.last_update = current_timestamp
                summoner_model.soloq_rank = league_data["soloq_rank"]
                summoner_model.soloq_lp = league_data["soloq_lp"]
                summoner_model.soloq_wins = league_data["soloq_wins"]
                summoner_model.soloq_losses = league_data["soloq_losses"]
                summoner_model.soloq_wr = league_data["soloq_wr"]
                summoner_model.flex_rank = league_data["flex_rank"]
                summoner_model.flex_lp = league_data["flex_lp"]
                summoner_model.flex_wins = league_data["flex_wins"]
                summoner_model.flex_losses = league_data["flex_losses"]
                summoner_model.flex_wr = league_data["flex_wr"]
                summoner_model.profile_icon_id = self.icon_id
                summoner_model.summoner_level = self.level

                db.session.commit()
            else:
                print("Summoner data is up-to-date.")
        
        else:
            # Add a new summoner to the database
            summoner_model = SummonerModel(
                summoner_puuid=self.puuid,
                summoner_id=self.id,
                summoner_name=self.summoner_name,
                region=self.region,
                last_update=current_timestamp,
                soloq_rank=league_data["soloq_rank"],
                soloq_lp=league_data["soloq_lp"],
                soloq_wins=league_data["soloq_wins"],
                soloq_losses=league_data["soloq_losses"],
                soloq_wr=league_data["soloq_wr"],
                flex_rank=league_data["flex_rank"],
                flex_lp=league_data["flex_lp"],
                flex_wins=league_data["flex_wins"],
                flex_losses=league_data["flex_losses"],
                flex_wr=league_data["flex_wr"],
                profile_icon_id=self.icon_id,
                summoner_level=self.level,
            )

            db.session.add(summoner_model)
            db.session.commit()
        
        
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
        last_match = MatchModel.query.filter_by(summoner_puuid=self.puuid).order_by(MatchModel.match_id.desc()).first()
            
        if last_match:
            recent_matches = [
                match_id for match_id in self.all_match_ids_this_season() if match_id > last_match.match_id
            ]
            if recent_matches:
                new_matches_data = self._matches_data(recent_matches)
                self.save_matches_data_to_db(new_matches_data)
        
        else:
            all_matches = self.all_match_ids_this_season()
            if all_matches:
                all_matches_data = self._matches_data(all_matches)
                self.save_matches_data_to_db(all_matches_data)
        
        matches = MatchModel.query.filter_by(summoner_puuid=self.puuid).all()
        matches_data = []
        
        for match in matches:
            match_data = {
                "summoner_puuid": match.summoner_puuid,
                "match_id": match.match_id,
                "champion_name": match.champion_name,
                "win": match.win,
                "kills": match.kills,
                "deaths": match.deaths,
                "assists": match.assists,
                "kda": match.kda,
                "cs": match.cs,
                "vision": match.vision,
                "summoner_spell1": match.summoner_spell1,
                "summoner_spell2": match.summoner_spell2,
                "item0": match.item0,
                "item1": match.item1,
                "item2": match.item2,
                "item3": match.item3,
                "item4": match.item4,
                "item5": match.item5,
                "item6": match.item6,
                "participant1_summoner_name": match.participant1_summoner_name,
                "participant2_summoner_name": match.participant2_summoner_name,
                "participant3_summoner_name": match.participant3_summoner_name,
                "participant4_summoner_name": match.participant4_summoner_name,
                "participant5_summoner_name": match.participant5_summoner_name,
                "participant6_summoner_name": match.participant6_summoner_name,
                "participant7_summoner_name": match.participant7_summoner_name,
                "participant8_summoner_name": match.participant8_summoner_name,
                "participant9_summoner_name": match.participant9_summoner_name,
                "participant10_summoner_name": match.participant10_summoner_name,
                "participant1_champion_name": match.participant1_champion_name,
                "participant2_champion_name": match.participant2_champion_name,
                "participant3_champion_name": match.participant3_champion_name,
                "participant4_champion_name": match.participant4_champion_name,
                "participant5_champion_name": match.participant5_champion_name,
                "participant6_champion_name": match.participant6_champion_name,
                "participant7_champion_name": match.participant7_champion_name,
                "participant8_champion_name": match.participant8_champion_name,
                "participant9_champion_name": match.participant9_champion_name,
                "participant10_champion_name": match.participant10_champion_name,
                "participant1_team_id": match.participant1_team_id,
                "participant2_team_id": match.participant2_team_id,
                "participant3_team_id": match.participant3_team_id,
                "participant4_team_id": match.participant4_team_id,
                "participant5_team_id": match.participant5_team_id,
                "participant6_team_id": match.participant6_team_id,
                "participant7_team_id": match.participant7_team_id,
                "participant8_team_id": match.participant8_team_id,
                "participant9_team_id": match.participant9_team_id,
                "participant10_team_id": match.participant10_team_id,
                "game_mode": match.game_mode,
                "game_duration": match.game_duration,
                "queue_id": match.queue_id,
                "team_position": match.team_position,
            }
            matches_data.append(match_data)
            
        return matches_data
    
    
    def save_matches_data_to_db(self, matches_data: dict) -> None:
        """Saves match data to the database.
        
            Args:
                matches_data: A dict containing match data for each match ID.
                
            Returns:
                None.
        """

        for match_id, game_data in matches_data.items():
            match_data = game_data["match_data"]
            summoner_data = game_data["summoner_data"]
            participants_data = game_data["participants_data"]
            
            new_match = MatchModel(
                summoner_puuid=summoner_data["summoner_puuid"],
                match_id=match_id,
                champion_name=summoner_data["champion_name"],
                win=summoner_data["win"],
                kills=summoner_data["kills"],
                deaths=summoner_data["deaths"],
                assists=summoner_data["assists"],
                kda=summoner_data["kda"],
                cs=summoner_data["cs"],
                vision=summoner_data["vision"],
                summoner_spell1=summoner_data["summoner_spell1"],
                summoner_spell2=summoner_data["summoner_spell2"],
                item0=summoner_data["item0"],
                item1=summoner_data["item1"],
                item2=summoner_data["item2"],
                item3=summoner_data["item3"],
                item4=summoner_data["item4"],
                item5=summoner_data["item5"],
                item6=summoner_data["item6"],
                participant1_summoner_name=participants_data[0]["summoner_name"],
                participant2_summoner_name=participants_data[1]["summoner_name"],
                participant3_summoner_name=participants_data[2]["summoner_name"],
                participant4_summoner_name=participants_data[3]["summoner_name"],
                participant5_summoner_name=participants_data[4]["summoner_name"],
                participant6_summoner_name=participants_data[5]["summoner_name"],
                participant7_summoner_name=participants_data[6]["summoner_name"],
                participant8_summoner_name=participants_data[7]["summoner_name"],
                participant9_summoner_name=participants_data[8]["summoner_name"],
                participant10_summoner_name=participants_data[9]["summoner_name"],
                participant1_champion_name=participants_data[0]["champion_name"],
                participant2_champion_name=participants_data[1]["champion_name"],
                participant3_champion_name=participants_data[2]["champion_name"],
                participant4_champion_name=participants_data[3]["champion_name"],
                participant5_champion_name=participants_data[4]["champion_name"],
                participant6_champion_name=participants_data[5]["champion_name"],
                participant7_champion_name=participants_data[6]["champion_name"],
                participant8_champion_name=participants_data[7]["champion_name"],
                participant9_champion_name=participants_data[8]["champion_name"],
                participant10_champion_name=participants_data[9]["champion_name"],
                participant1_team_id=participants_data[0]["team_id"],
                participant2_team_id=participants_data[1]["team_id"],
                participant3_team_id=participants_data[2]["team_id"],
                participant4_team_id=participants_data[3]["team_id"],
                participant5_team_id=participants_data[4]["team_id"],
                participant6_team_id=participants_data[5]["team_id"],
                participant7_team_id=participants_data[6]["team_id"],
                participant8_team_id=participants_data[7]["team_id"],
                participant9_team_id=participants_data[8]["team_id"],
                participant10_team_id=participants_data[9]["team_id"],
                game_mode=match_data["game_mode"],
                game_duration=match_data["game_duration"],
                queue_id=match_data["queue_id"],
                team_position=summoner_data["team_position"]
            )
            
            db.session.add(new_match)
            db.session.commit()
            
            

        
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
                        "team_position": participant["teamPosition"],
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
        # Crea una tabla temporal con los datos agregados de matches
        
        temp_stats = db.session.query(
            MatchModel.summoner_puuid,
            MatchModel.champion_name,
            db.func.count().label("matches_played"),
            db.func.sum(MatchModel.win).label("wins"),
            (db.func.count() - db.func.sum(MatchModel.win)).label("losses"),
            (db.func.round((db.func.sum(MatchModel.win) * 100.0) / db.func.count())).label("wr"),
            (db.func.round((db.func.sum(MatchModel.kills) + db.func.sum(MatchModel.assists)) / (db.func.sum(MatchModel.deaths) + 0.001), 2)).label("kda"),
            (db.func.round(db.func.sum(MatchModel.kills) * 1.0 / db.func.count(), 1)).label("kills"),
            (db.func.round(db.func.sum(MatchModel.deaths) * 1.0 / db.func.count(), 1)).label("deaths"),
            (db.func.round(db.func.sum(MatchModel.assists) * 1.0 / db.func.count(), 1)).label("assists"),
            (db.func.round(db.func.sum(MatchModel.cs) * 1.0 / db.func.count())).label("cs")
        ).filter(MatchModel.queue_id.in_([420, 440])).group_by(MatchModel.summoner_puuid, MatchModel.champion_name).subquery()

        # Insertar los registros de la tabla temporal en champion_stats
        insert_stat = ChampionStatsModel.__table__.insert().from_select(
            [
                ChampionStatsModel.summoner_puuid,
                ChampionStatsModel.champion_name,
                ChampionStatsModel.matches_played,
                ChampionStatsModel.wins,
                ChampionStatsModel.losses,
                ChampionStatsModel.wr,
                ChampionStatsModel.kda,
                ChampionStatsModel.kills,
                ChampionStatsModel.deaths,
                ChampionStatsModel.assists,
                ChampionStatsModel.cs,
            ],
            temp_stats.select().where(
                db.not_(
                    db.session.query(ChampionStatsModel).filter(
                        ChampionStatsModel.summoner_puuid == temp_stats.c.summoner_puuid,
                        ChampionStatsModel.champion_name == temp_stats.c.champion_name
                    ).exists()
                )
            )
        )

        db.session.execute(insert_stat)
        db.session.commit()
    
    def top_champions_data(self, top=5):
        top_champions_query = db.session.query(
            ChampionStatsModel.champion_name,
            ChampionStatsModel.matches_played,
            ChampionStatsModel.wr,
            ChampionStatsModel.kda,
            ChampionStatsModel.kills,
            ChampionStatsModel.deaths,
            ChampionStatsModel.assists,
            ChampionStatsModel.cs
        ).filter(
            ChampionStatsModel.summoner_puuid == self.puuid
        ).order_by(
            ChampionStatsModel.matches_played.desc(),
            ChampionStatsModel.wr.desc(),
            ChampionStatsModel.kda.desc()
        ).limit(top)

        top_champions_list = top_champions_query.all()

        top_champions = []
        for champion in top_champions_list:
            champion_dict = {
                "champion_name": champion.champion_name,
                "matches_played": champion.matches_played,
                "wr": champion.wr,
                "kda": champion.kda,
                "kills": champion.kills,
                "deaths": champion.deaths,
                "assists": champion.assists,
                "cs": champion.cs,
            }
            top_champions.append(champion_dict)

        return top_champions
        
        
    def role_data(self) -> dict:
        role_data_query = db.session.query(
            MatchModel.team_position
        ).filter(
            MatchModel.summoner_puuid == self.puuid
        )

        role_data = role_data_query.all()
        role_counts = {
            "TOP": 0,
            "JUNGLE": 0,
            "MIDDLE": 0,
            "BOTTOM": 0,
            "UTILITY": 0,
        }
        for role in role_data:
            role = role[0]
            if role in role_counts:
                role_counts[role] += 1

        return role_counts
        
        


# TODO Dividir la clase Summoner en varias subclases
# TODO Ver como puedo meterle la capa de cache para que tire de ahi en vez de database cuando actualizo la web.