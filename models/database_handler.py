import time

from .db_models import db, SummonerModel, MatchModel



UPDATE_THRESHOLD = 3600


class DatabaseHandler:
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