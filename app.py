import os

from flask import Flask, jsonify
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS

from db import db
from resources.user import blp as UserBlueprint
from resources.bets import blp as BetsBlueprint
from resources.matches import blp as MatchesBlueprint
from resources.groups import blp as GroupsBlueprint
from resources.admin.admin import blp as AdminBlueprint
from models.blocklist import BlocklistModel
from schedulers import initialize_schedulers


def create_app(db_url=None):

    # Initialize Flask application
    app = Flask(__name__)

    # Enable CORS (Cross-Origin Resource Sharing) for all routes
    enable_cors(app)

    # Load environment variables from .env file
    load_dotenv()

    # Load configuration settings for the Flask app
    load_configuration(app, db_url)

    # Initialize and configure the database
    initialize_database(app)

    # Initialize JWT (JSON Web Tokens) authentication
    initialize_jwt(app)

    # Initialize background job schedulers
    initialize_schedulers(app)

    # Register blueprints (modular components of the application)
    register_blueprints(app)

    # Return the configured Flask application instance
    return app


def enable_cors(app):
    CORS(app)

def load_configuration(app, db_url):
    app.config["API_TITLE"] = "Premier League REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_SECRET_KEY"] = 'adam' #will be changed later
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

def initialize_database(app):

    db.init_app(app)
    with app.app_context():
        db.create_all()
    migrate = Migrate(app, db)

def initialize_jwt(app):

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

def register_blueprints(app):
    api = Api(app)
    
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(BetsBlueprint)
    api.register_blueprint(MatchesBlueprint)
    api.register_blueprint(GroupsBlueprint)
    api.register_blueprint(AdminBlueprint)
