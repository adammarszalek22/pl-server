import os
import redis

from flask import Flask, jsonify
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
from rq import Queue
from rq_scheduler import Scheduler
from datetime import datetime

import models

from db import db
from resources.user import blp as UserBlueprint
from resources.bets import blp as BetsBlueprint
from models.blocklist import BlocklistModel
from tasks import example1

from flask_apscheduler import APScheduler
from get_matches import matches


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()
    connection = redis.from_url(
        os.getenv("REDIS_URL")
    )
    app.queue = Queue("example", connection=connection)
    # app.scheduler = Scheduler(queue = app.queue, connection = app.queue.connection)
    # scheduler = Scheduler('example', connection=connection)
    # scheduler.enqueue_in(timedelta(seconds=10), example)
    # scheduler.schedule(
    #     scheduled_time=datetime.utcnow(),
    #     func=example,
    #     interval=10,
    #     repeat=10
    #     )
    #scheduler = APScheduler()
    #scheduler.add_job(id = 'Description of cron job', func = example1, trigger = 'interval', seconds = 10)
    #scheduler.start()
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
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

    return app