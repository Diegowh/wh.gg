from flask import Flask, render_template, request
import os
from my_code.summoner import Summoner


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(basedir, 'data.db'))

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('test.html')

@app.route('/get_summoner', methods=['POST'])
def get_summoner():
    summoner_name = request.form['summoner_name']
    api_key = "RGAPI-00bdcbf0-4f11-4b53-a7f7-3e1cb05583b3"
    region = "EUW1"
    
    summoner = Summoner(summoner_name, api_key, region)
    
    
    data_to_show = {
        "summoner_name": summoner.summoner_name,
        "soloq_rank": summoner.soloq_rank, 
        "flex_rank": summoner.flex_rank,
    }
    return render_template('test.html', summoner_name=summoner_name)






if __name__ == '__main__':
    app.run(debug=True)