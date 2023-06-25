from db import db


class MatchesModel(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(80), unique=True)
    goal1 = db.Column(db.Integer)
    goal2 = db.Column(db.Integer)
