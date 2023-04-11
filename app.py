from flask import Flask, render_template, request
import os
from my_code.summoner import Summoner
from urllib.parse import quote


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(basedir, 'data.db'))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('test.html')

@app.route('/get_summoner', methods=['POST'])
def get_summoner():
    summoner_name = quote(request.form['summoner_name'])
    api_key = "RGAPI-13f2c40d-9832-4434-afe5-d7607e66bc36"
    region = "EUW1"
    
    summoner = Summoner(summoner_name, api_key, region)
    summoner_data = summoner.league_data()
    
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
                        flex_wr=summoner_data['flex_wr']
                        )



if __name__ == '__main__':
    app.run(debug=True)