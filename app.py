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

from db import db
from resources.user import blp as UserBlueprint
from resources.bets import blp as BetsBlueprint
from resources.matches import blp as MatchesBlueprint
from resources.groups import blp as GroupsBlueprint
from resources.admin.admin import blp as AdminBlueprint
from models.blocklist import BlocklistModel
from db import db
from models import MatchesModel, UserModel, GroupsModel

from flask_apscheduler import APScheduler


def create_app(db_url=None):
    
    app = Flask(__name__)
    load_dotenv()
    
    matches_scheduler = APScheduler()
    scheduler = APScheduler()
    group_pos_scheduler = APScheduler()

    # to be fixed, don't want nested functions
    def get_matches():
        # getting match info from the fantasy premier league API
        with app.app_context():
            url = 'https://fantasy.premierleague.com/api/fixtures/'
            request = requests.get(url)
            response = json.loads(request.content)
            for i in response:
                match = MatchesModel.query.filter(
                    MatchesModel.match_id == str(i["code"])
                    ).first()
                if match:
                    # if match is already in database, update match info
                    match.finished = i["finished"]
                    match.goal1 = i["team_h_score"]
                    match.goal2 = i["team_a_score"]
                    db.session.add(match)
                    db.session.commit()
                else:
                    # otherwise add match to the database
                    # (usually all matches are added at the start of the season)
                    match = MatchesModel(
                        match_id = i["code"],
                        goal1 = i["team_h_score"],
                        goal2 = i["team_a_score"],
                        start_time = i["kickoff_time"],
                        finished = i["finished"]
                    )
                    db.session.add(match)
                    db.session.commit()
        
    def compare_scores():
        # this function compares users' scores to actual scores and awards points
        with app.app_context():

            def compare(a, b, c, d):
                # helper function
                # a, b - predicted score; c, d - actual score
                if a == c and b == d:
                    # 3 points for guessing the exact score
                    return 3
                # 1 point for guessing the winner or draw ↓
                if a > b and c > d:
                    return 1
                if b > a and d > c:
                    return 1
                if a == b and c == d:
                    return 1
                # else 0 points
                return 0
            
            users = UserModel.query.all()
            for user in users:
                # for every match score prediction made by user
                for bet in user.bets:
                    match = MatchesModel.query.filter(MatchesModel.match_id == bet.match_id).first()
                    if match and match.finished == True and bet.done == "no":
                        points = compare(bet.goal1, bet.goal2, match.goal1, match.goal2)
                        # adding points
                        user.points += points
                        if points == 3:
                            user.three_pointers += 1
                        elif points == 1:
                            user.one_pointers += 1
                        # changing to 'yes' so that next time this game is skipped 
                        bet.done = "yes"
                        db.session.add(user)
                        db.session.commit()
            # positions function is run at the end of this function and not in the scheduler
            # this is to avoid functions executing at the same time as they both interact with the UserModel
            positions()
        
    def positions():
        # this function decides users' standings in the main league
        with app.app_context():
            # creating a dict with all users
            positions = {}
            users = UserModel.query.all()
            for user in users:
                positions[user.id] = {}
                positions[user.id]["points"] = int(user.points)
                positions[user.id]["three_pointers"] = int(user.three_pointers)
                positions[user.id]["one_pointers"] = int(user.one_pointers)
            # sorting the dict by points, if 2 users have the same amount of points then whoever has more three pointers is higher
            positions = {k: v for k, v in sorted(positions.items(), key=lambda item: (item[1]["points"], item[1]["three_pointers"]), reverse=True)}

            standing = 1
            for player_id in positions.keys():
                # assigning the standings to the users
                user = UserModel.query.get_or_404(player_id)
                user.position = standing
                db.session.add(user)
                db.session.commit()
                standing += 1
    
    def groups_positions():
        # same as the positions() function but for each small league 
        with app.app_context():
            groups = GroupsModel.query.all()
            for group in groups: 
                positions = {}
                for user in group.user:
                    positions[user.id] = {}
                    positions[user.id]["points"] = int(user.points)
                    positions[user.id]["three_pointers"] = int(user.three_pointers)
                    positions[user.id]["one_pointers"] = int(user.one_pointers)
                positions = {k: v for k, v in sorted(positions.items(), key=lambda item: (item[1]["points"], item[1]["three_pointers"]), reverse=True)}
                pos = []
                for i in positions.keys():
                    pos.append(i)
                pos_string = ' '.join(map(str, pos))
                group.positions = pos_string
                db.session.add(group)
                db.session.commit()

    scheduler_time = 100
    matches_scheduler.add_job(id = 'Updating matches',
                      func = get_matches,
                      trigger = 'interval',
                      seconds = scheduler_time)
    scheduler.add_job(id = 'Comparing scores',
                      func = compare_scores,
                      trigger = 'interval',
                      seconds = scheduler_time)
    group_pos_scheduler.add_job(id = 'Group positions',
                      func = groups_positions,
                      trigger = 'interval',
                      seconds = scheduler_time)
    
    matches_scheduler.start()
    scheduler.start()
    group_pos_scheduler.start()

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

    app.config["JWT_SECRET_KEY"] = 'adam' #will be changed later
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        blocklist_item = BlocklistModel.query.get(jwt_payload['jti'])
        return blocklist_item != None
    
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
        if identity == 'adam1234':
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
    api.register_blueprint(GroupsBlueprint)
    api.register_blueprint(AdminBlueprint)

    return app