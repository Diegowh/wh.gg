from .db_models import db, ChampionStatsModel, MatchModel
from sqlalchemy import cast, Numeric, Float


RECENT_MATCHES_LIMIT = 10


class MatchStats:
    def recent_matches_data(self) -> list:
        matches_data = self._matches_data_from_db()
        self.update_champion_stats()

        def match_id_key(match_data):
            return match_data["match_id"]

        matches_data.sort(key=match_id_key, reverse=True)
        recent_matches_data = matches_data[:RECENT_MATCHES_LIMIT]

        return recent_matches_data
    
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
            (db.func.round(cast(db.func.sum(MatchModel.win) * 100.0, Numeric) / db.func.count())).label("wr"),
            (db.func.round(cast(db.func.sum(MatchModel.kills) + db.func.sum(MatchModel.assists), Numeric) / cast(db.func.sum(MatchModel.deaths) + 0.001, Numeric), 2)).label("kda"),
            (db.func.round(cast(db.func.sum(MatchModel.kills) * 1.0, Numeric) / db.func.count(), 1)).label("kills"),
            (db.func.round(cast(db.func.sum(MatchModel.deaths) * 1.0, Numeric) / db.func.count(), 1)).label("deaths"),
            (db.func.round(cast(db.func.sum(MatchModel.assists) * 1.0, Numeric) / db.func.count(), 1)).label("assists"),
            (db.func.round(cast(db.func.sum(MatchModel.cs) * 1.0, Numeric) / db.func.count())).label("cs")
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