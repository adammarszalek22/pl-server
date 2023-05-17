from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import BetsModel, BlocklistModel
from schemas import BetsSchema, PlainBetsSchema, BetsUpdateSchema

blp = Blueprint("Bets", "bets", description="Operations on bets")


@blp.route("/bet/<int:bet_id>")
class Bet(MethodView):
    @jwt_required()
    @blp.response(200, BetsSchema)
    def get(self, bet_id):
        bet = BetsModel.query.get_or_404(bet_id)
        return bet

    @jwt_required()
    def delete(self, bet_id):
        jwt = get_jwt()
        if not jwt.get('is_admin'):
            abort(401, message='Admin privilage required')
        bet = BetsModel.query.get_or_404(bet_id)
        db.session.delete(bet)
        db.session.commit()
        return {"message": "Bet deleted."}
    '''
    @jwt_required()
    @blp.arguments(BetsUpdateSchema)
    @blp.response(200, BetsSchema)
    def put(self, bet_data, bet_id):
        bet = BetsModel.query.get(bet_id)
        id = get_jwt()["sub"]
        if id == bet_data["user_id"]:
            if bet:
                bet.goal1 = bet_data["goal1"]
                bet.goal2 = bet_data["goal2"]
                db.session.add(bet)
                db.session.commit()
            else:
                abort(404, message="Bet not found.")
        else:
            abort(401, message="Cannot update other users\' bets.")

        return bet
    '''

@blp.route("/bet")
class BetList(MethodView):
    @jwt_required()
    @blp.response(200, BetsSchema(many=True))
    def get(self):
        return BetsModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(BetsSchema)
    @blp.response(201, BetsSchema)
    def post(self, bet_data):
        bet = BetsModel(**bet_data)
        id = get_jwt()['sub']
        another_bet = BetsModel.query.filter(
            BetsModel.match_id == bet_data["match_id"]
        ).first()
        if bet_data["user_id"] == id:
            if another_bet:
                abort(500, message="Bet already exists")
            else:
                try:
                    db.session.add(bet)
                    db.session.commit()
                except SQLAlchemyError:
                    abort(500, message="An error occurred while inserting the bet.")  
        else:
            abort(401, message="Cannot post bets for other users")
        return bet

    @jwt_required()
    @blp.arguments(BetsUpdateSchema)
    @blp.response(200, BetsSchema)
    def put(self, bet_data):
        #bet = BetsModel(**bet_data)
        bet = BetsModel.query.filter(
            BetsModel.match_id == bet_data["match_id"]
        ).first()
        id = get_jwt()["sub"]
        if id == bet_data["user_id"]:
            if bet:
                bet.goal1 = bet_data["goal1"]
                bet.goal2 = bet_data["goal2"]
                db.session.add(bet)
                db.session.commit()
            else:
                bet = BetsModel(**bet_data)
                db.session.add(bet)
                db.session.commit()
        else:
            abort(401, message="Cannot update other users\' bets.")
        return bet