from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from db import db
from models import MatchesModel
from schemas import MatchesSchema

blp = Blueprint("Matches", "matches", description="Operations on matches")


@blp.route("/matches")
class MatchesList(MethodView):
    
    @jwt_required()
    @blp.response(200, MatchesSchema(many=True))
    def get(self):

        return MatchesModel.query.all()

@blp.route("/matches/<int:match_id>")
class MatchesList(MethodView):

    @jwt_required()
    @blp.response(200, MatchesSchema)
    def get(self, match_id):

        match =  MatchesModel.query.filter(
            MatchesModel.match_id == str(match_id)
        ).first()

        return match