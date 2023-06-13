import os
import redis
import requests
import json

from flask import Flask, jsonify
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
from rq import Queue

from db import db
from resources.user import blp as UserBlueprint
from resources.bets import blp as BetsBlueprint
from resources.matches import blp as MatchesBlueprint
from models.blocklist import BlocklistModel
from db import db
from models import MatchesModel, UserModel

from flask_apscheduler import APScheduler


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()
    connection = redis.from_url(
        os.getenv("REDIS_URL")
    )
    app.queue = Queue("example", connection=connection)
    # scheduler = APScheduler()
    
    # def get_matches():
    #     with app.app_context():
    #         url = 'https://fantasy.premierleague.com/api/fixtures/'
    #         request = requests.get(url)
    #         response = json.loads(request.content)
    #         for i in response:
    #             if MatchesModel.query.filter(MatchesModel.match_id == str(i["code"])).first():
    #                 pass
    #             else:
    #                 if i["finished"] == True:
    #                     print('finished')
    #                     match = MatchesModel(
    #                         match_id = i["code"],
    #                         goal1 = i["team_h_score"],
    #                         goal2 = i["team_a_score"],
    #                         done = "no"
    #                     )
    #                     db.session.add(match)
    #                     db.session.commit()
    #         print(MatchesModel.query.all())
    #         print('done')
        
    # def compare_guesses():
    #     with app.app_context():
    #         def compare(a, b, c, d):
    #             if a == c and b == d:
    #                 return 3
    #             elif a > b and c > d:
    #                 return 1
    #             elif b > a and d > c:
    #                 return 1
    #             elif a == b and c == d:
    #                 return 1
    #             else:
    #                 return 0
    #         users = UserModel.query.all()
    #         for user in users:
    #             for bet in user.bets:
    #                 match = MatchesModel.query.filter(MatchesModel.match_id == bet.match_id).first()
    #                 if match and match.done == "no":
    #                     points = compare(bet.goal1, bet.goal2, match.goal1, match.goal2)
    #                     user.points = user.points + points
    #                     match.done = "yes"
    #                     db.session.add(user)
    #                     db.session.add(match)
    #                     db.session.commit()
    #         print('DONE')
    
    # scheduler.add_job(id = 'Updating matches',
    #                   func = get_matches,
    #                   trigger = 'interval',
    #                   seconds = 100)
    # scheduler.add_job(id = 'Comparing guesses to actual scores',
    #                   func = compare_guesses,
    #                   trigger = 'interval',
    #                   seconds = 120)
    # scheduler.start()

    app.config["API_TITLE"] = "Premier League REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = 'adam'
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        blocklist_item = BlocklistModel.query.get(jwt_payload['jti'])
        if blocklist_item:
            return True
        return False
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return(
            jsonify(
            {'description': 'The token has been revoked',
             'error': 'token_revoked'}
            ),
            401
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return(
            jsonify(
            {
                'description': 'The token is not fresh',
                'error': 'fresh_token_required'
            }
            ),
            401
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {'is_admin': True}
        return {'is_admin': False}


    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return(
            jsonify(
            {'message': 'The token has expired', 'error': 'token_expired'}
            ),
            401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(
            jsonify(
            {'message': 'Signature verification failed.', 'error': 'invalid_token'}
            ),
            401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify(
            {'description': 'Request does not contain an access token', 
             'error': 'authorization_required'}
            ),
            401
        )
    
    with app.app_context():
        db.create_all()
    
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(BetsBlueprint)
    api.register_blueprint(MatchesBlueprint)

    return app