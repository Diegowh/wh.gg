import roman

from typing import Dict, Any



class RankedData:
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