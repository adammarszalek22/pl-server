from db import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    
    points = db.Column(db.Integer)
    position = db.Column(db.Integer)
    three_pointers = db.Column(db.Integer)
    one_pointers = db.Column(db.Integer)

    bets = db.relationship("BetsModel", back_populates="user", lazy="dynamic")
    groups = db.relationship("GroupsModel", back_populates="user", lazy="dynamic", secondary="users_groups")