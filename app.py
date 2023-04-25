from flask import Flask, render_template, request
import os
from models.summoner_data import SummonerData
from urllib.parse import quote
from dotenv import load_dotenv
import config
from models.db_models import db
from flask_migrate import Migrate
from utils.utils import get_game_type


load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)
    
    return app


app = create_app()


@app.route('/summoners/<region>/<summoner_name>', methods=['GET'])
def summoner_info(region, summoner_name):
    api_key = os.getenv("RIOT_API_KEY")
    
    
    summoner = SummonerData(summoner_name, api_key, region)
    summoner_data = summoner.league_data()
    recent_matches_data = summoner.recent_matches_data()
    top_champs_data = summoner.top_champions_data()
    role_data = summoner.role_data()

    summoner_data = {
        "summoner_name": summoner_name,
        "profile_icon_id": summoner_data["profile_icon_id"],
        "summoner_level": summoner_data["summoner_level"],
        "soloq": {
            "rank": summoner_data["soloq_rank"].title(),
            "lp": summoner_data["soloq_lp"],
            "wins": summoner_data["soloq_wins"],
            "losses": summoner_data["soloq_losses"],
            "wr": summoner_data["soloq_wr"],
        },
        "flex": {
            "rank": summoner_data["flex_rank"].title(),
            "lp": summoner_data["flex_lp"],
            "wins": summoner_data["flex_wins"],
            "losses": summoner_data["flex_losses"],
            "wr": summoner_data["flex_wr"],
        },
    }

    champions_played = [
        {
            "champion_name": champ["champion_name"],
            "cs": champ["cs"],
            "kda": champ["kda"],
            "kills": champ["kills"],
            "deaths": champ["deaths"],
            "assists": champ["assists"],
            "wr": champ["wr"],
            "games_played": champ["matches_played"],
        }
        for champ in top_champs_data
    ]
    
    recent_matches = [
        {
            "game_type": get_game_type(match["queue_id"]),
            "game_mode": match["game_mode"],
            "queue_id": match["queue_id"],
            "game_duration": match["game_duration"],
            "win": match["win"],
            "champion_name": match["champion_name"],
            "item_ids": [
                match["item0"], 
                match["item1"], 
                match["item2"], 
                match["item3"], 
                match["item4"], 
                match["item5"], 
                match["item6"]
                ],
            "summoner_spell_ids": [
                match["summoner_spell1"], 
                match["summoner_spell2"]],
            "kills": int(match["kills"]),
            "deaths": int(match["deaths"]),
            "assists": int(match["assists"]),
            "cs": match["cs"],
            "vision": match["vision"],
            "participant_summoner_names": [match["participant1_summoner_name"], match["participant2_summoner_name"], match["participant3_summoner_name"], match["participant4_summoner_name"], match["participant5_summoner_name"], match["participant6_summoner_name"], match["participant7_summoner_name"], match["participant8_summoner_name"], match["participant9_summoner_name"], match["participant10_summoner_name"]],
            "participant_champion_names": [match["participant1_champion_name"], match["participant2_champion_name"], match["participant3_champion_name"], match["participant4_champion_name"], match["participant5_champion_name"], match["participant6_champion_name"], match["participant7_champion_name"], match["participant8_champion_name"], match["participant9_champion_name"], match["participant10_champion_name"]
            ],
        }
        for match in recent_matches_data
    ]

    
    return render_template('index.html', 
                        summoner_name=summoner_name,
                        summoner_data=summoner_data,
                        champions_played=champions_played,
                        recent_matches=recent_matches,
                        role_data=role_data,
                        region=region
                        )
    
    
@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=config.DEBUG)

