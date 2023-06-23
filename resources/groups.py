from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import GroupsModel, UserModel, UsersGroups
from schemas import GetGroupsSchema, CreateGroupsSchema, JoinGroupsSchema

blp = Blueprint("Groups", "groups", description = "User's groups")

'''
ADD ERROR HANDLING LATER

POST - create group (and become an admin) and give it a name
PUT - join group with your user id and group unique id
GET - get unique id to share with others (so that they can join)
GET_ALL

'''

@blp.route("/all_groups")
class AllGroups(MethodView):

    @jwt_required()
    @blp.response(200, GetGroupsSchema(many=True))
    def get(self):
        groups = GroupsModel.query.all()
        return groups

@blp.route("/groups")
class Group(MethodView):

    @jwt_required()
    @blp.arguments(GetGroupsSchema)
    @blp.response(200, GetGroupsSchema)
    def get(self, group_data):

        group = GroupsModel.query.filter(
            GroupsModel.id == group_data["id"]
        ).first()

        return group
    
    @jwt_required()
    @blp.arguments(CreateGroupsSchema)
    @blp.response(201, CreateGroupsSchema)
    def post(self, group_data):

        newgroup = GroupsModel(**group_data)
        db.session.add(newgroup)
        db.session.commit()

        return newgroup

    @jwt_required()
    @blp.arguments(JoinGroupsSchema)
    @blp.response(201, JoinGroupsSchema)
    def put(self, group_data):

        group = GroupsModel.query.filter(
            GroupsModel.id == group_data["id"]
        ).first()
        user = UserModel.query.get_or_404(group_data["user_id"])


        group.user.append(user)
        db.session.add(group)
        db.session.commit()

        return group

