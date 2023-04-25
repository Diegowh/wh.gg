from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

import config
from models.db_models import db
from routes.summoner import summoner_bp
from routes.main import main_bp


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
app.register_blueprint(summoner_bp)
app.register_blueprint(main_bp)


if __name__ == '__main__':
    app.run(debug=config.DEBUG)