from db import db


class MatchesModel(db.Model):
    __tablename__ = 'matches'

    match_id = db.Column(db.String(80))
    goal1 = db.Column(db.Integer)
    goal2 = db.Column(db.Integer)
    done = db.Column(db.String(10))
