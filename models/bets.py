from db import db


class BetsModel(db.Model):
    __tablename__ = 'bets'

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.String(80))
    goal1 = db.Column(db.Integer)
    goal2 = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False)
    user = db.relationship("UserModel", back_populates="bets")
