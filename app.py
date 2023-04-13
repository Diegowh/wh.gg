from flask import Flask, render_template, request
import os
from my_code.summoner import Summoner
from urllib.parse import quote


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(basedir, 'data.db'))

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        summoner_name = request.form['summoner_name']
        api_key = "RGAPI-b9e033aa-3fdc-40e5-a74b-6d7512055866"
        region = "EUW1"
        
        summoner = Summoner(summoner_name, api_key, region)
        summoner_data = summoner.league_data()
        matches_data = summoner.recent_matches_data()
        top_champs_data = summoner.top_champions_data()
        
        return render_template('test.html', 
                            summoner_name=summoner_name, 
                            soloq_rank=summoner_data['soloq_rank'],
                            soloq_lp=summoner_data['soloq_lp'],
                            soloq_wins=summoner_data['soloq_wins'],
                            soloq_losses=summoner_data['soloq_losses'],
                            soloq_wr=summoner_data['soloq_wr'],
                            flex_rank=summoner_data['flex_rank'],
                            flex_lp=summoner_data['flex_lp'],
                            flex_wins=summoner_data['flex_wins'],
                            flex_losses=summoner_data['flex_losses'],
                            flex_wr=summoner_data['flex_wr'],
                            champion_played_0=matches_data[0]["champion_name"],
                            champion_played_1=matches_data[1]["champion_name"],
                            champion_played_2=matches_data[2]["champion_name"],
                            champion_played_3=matches_data[3]["champion_name"],
                            champion_played_4=matches_data[4]["champion_name"],
                            top_champion_1=top_champs_data,
                            )
    else:
        return render_template("test.html")

if __name__ == '__main__':
    app.run(debug=True)
    
    
