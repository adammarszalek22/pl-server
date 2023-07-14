from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import BetsModel, UserModel, MatchesModel
from schemas import BetsSchema, MultipleUpdateBetsSchema
from date_time import convert_to_datetime, has_passed

blp = Blueprint("Bets", "bets", description="Operations on bets")


@blp.route("/bet/<int:bet_id>")
class Bet(MethodView):

    # Anyone who is logged in
    @jwt_required()
    @blp.response(200, BetsSchema)
    def get(self, bet_id):
        bet = BetsModel.query.get_or_404(bet_id)
        return bet
    
    # Anyone who is logged in can delete their own bets only
    @jwt_required()
    def delete(self, bet_id):
        user_id = get_jwt()["sub"]
        bet = BetsModel.query.filter(BetsModel.user_id == user_id,
                                     BetsModel.id == bet_id).first()
        if bet:
            db.session.delete(bet)
            db.session.commit()
            return {"message": "Bet deleted."}
        else:
            return {"message": "Bet not found."}

@blp.route("/bet")
class BetList(MethodView):

    # The user can delete their own bets only
    @jwt_required()
    def delete(self):
        user_id = get_jwt()['sub']
        user = UserModel.query.filter(UserModel.id == user_id).first()
        for bet in user.bets:
            db.session.delete(bet)
            db.session.commit()
        return {"message": "All bets deleted."}
    
    # Anyone who is logged in can get all bets
    @jwt_required()
    @blp.response(200, BetsSchema(many=True))
    def get(self):
        return BetsModel.query.all()
    
    # Users can post their own bets
    @jwt_required(fresh=True)
    @blp.arguments(BetsSchema)
    @blp.response(201, BetsSchema)
    def post(self, bet_data):

        bet = BetsModel(**bet_data)

        match_ = MatchesModel.query.filter(
            MatchesModel.match_id == bet_data["match_id"]
        ).first()

        if has_passed(convert_to_datetime(match_.start_time)):
            abort(405, message="Cannot post bet after match has started.")

        user_id = get_jwt_identity()

        another_bet = BetsModel.query.filter(
            BetsModel.match_id == bet_data["match_id"],
            BetsModel.user_id == user_id
        ).first()

        if another_bet:
            abort(500, message="Bet already exists")
        else:
            try:
                db.session.add(bet)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="An error occurred while inserting the bet.")
        return bet

    @jwt_required()
    @blp.arguments(BetsSchema)
    @blp.response(200, BetsSchema)
    def put(self, bet_data):
        # Users can update their own bets
        user_id = get_jwt_identity()

        match_ = MatchesModel.query.filter(
            MatchesModel.match_id == bet_data["match_id"]
        ).first()

        bet = BetsModel.query.filter(
            BetsModel.match_id == bet_data["match_id"],
            BetsModel.user_id == user_id
        ).first()

        if has_passed(convert_to_datetime(match_.start_time)):
            abort(405, message="Cannot update the bet after match has started.")

        if bet:
            bet.goal1 = bet_data["goal1"]
            bet.goal2 = bet_data["goal2"]
            bet.done = bet_data["done"]
            db.session.add(bet)
            db.session.commit()
        else:
            bet = BetsModel(**bet_data)
            if has_passed(convert_to_datetime(match_.start_time)):
                abort(405, message="Cannot update the bet after match has started.")
            db.session.add(bet)
            db.session.commit()

        return bet

@blp.route("/bet_by_user_id")
class BetList(MethodView):
    
    # Anyone who is logged in can get all their bets
    @jwt_required()
    @blp.response(200, BetsSchema(many=True))
    def get(self):
        user_id = get_jwt_identity()
        return BetsModel.query.filter(
            BetsModel.user_id == user_id
        ).all()

@blp.route("/multiple_bets_update")
class BetList(MethodView):

    @jwt_required()
    @blp.arguments(MultipleUpdateBetsSchema)
    @blp.response(200, MultipleUpdateBetsSchema)
    def put(self, bet_data):
        # Users can update their own bets
        user_id = get_jwt_identity()

        all_bets = []

        i = -1
        for code in bet_data["match_id"]:
            i += 1
            now_bet = BetsModel.query.filter(
                BetsModel.match_id == code,
                BetsModel.user_id == user_id
            ).first()
            match_ = MatchesModel.query.filter(
                MatchesModel.match_id == code
                ).first()
            if has_passed(convert_to_datetime(match_.start_time)):
                abort(405, message="Cannot update the bet after match has started.")
            if now_bet:
                now_bet.goal1 = bet_data["goal1"][i]
                now_bet.goal2 = bet_data["goal2"][i]
                now_bet.done = 'no'
                all_bets.append(now_bet)
                db.session.add(now_bet)
                db.session.commit()
            else:
                new_bet = BetsModel()
                new_bet.user_id = user_id
                new_bet.match_id = code
                new_bet.goal1 = bet_data["goal1"][i]
                new_bet.goal2 = bet_data["goal2"][i]
                new_bet.done = 'no'
                all_bets.append(new_bet)
                db.session.add(new_bet)
                db.session.commit()

        return all_bets