from db import db


class GroupsModel(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False)
    
    user = db.relationship("UserModel", back_populates="groups", secondary="users_groups")