from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256

from db import db
from models import GroupsModel, UserModel, UsersGroups
from schemas import GetGroupsSchema, CreateGroupsSchema, JoinGroupsSchema
from schemas import DeleteGroupSchema, PlainUserSchema, DeleteUserFromGroup, MyGroupSchema

blp = Blueprint("Groups", "groups", description = "User's groups")


@blp.route("/all_groups")
class AllGroups(MethodView):

    @jwt_required()
    @blp.response(200, GetGroupsSchema(many=True))
    def get(self):

        groups = GroupsModel.query.all()

        return groups
    
    @jwt_required()
    @blp.arguments(PlainUserSchema)
    def delete(self, user_data):

        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and user_data["username"] == "adamgswhctp"\
        and pbkdf2_sha256.verify(user_data["password"], user.password):
            groups = GroupsModel.query.all()
            for group in groups:
                db.session.delete(group)
                db.session.commit()
            return {"message": "All groups deleted", "code": 200}
        elif not user:
            abort(404, message="User not found")
        elif user_data["username"] != "adamgswhctp":
            abort(401, message="Unauthorized - user is not an admin")
        else:
            abort(401, message="Unauthorized - wrong password")

@blp.route('/my_groups')
class MyGroup(MethodView):

    @jwt_required()
    @blp.response(200, GetGroupsSchema(many=True))
    def get(self):
        
        user_id = get_jwt_identity()

        groups = GroupsModel.query.filter(
            GroupsModel.admin_id == user_id
        ).all()

        return groups
    
@blp.route('/groups_im_in')
class MyGroup(MethodView):

    @jwt_required()
    @blp.response(200, GetGroupsSchema(many=True))
    def get(self):
        
        user_id = get_jwt_identity()

        users_groups = UsersGroups.query.filter(
            UsersGroups.user_id == user_id
        ).all()

        group_ids = []
        for row in users_groups:
            group_ids.append(row.group_id)
        group_ids = tuple(group_ids)


        groups = GroupsModel.query.filter(
            GroupsModel.id.in_(group_ids),
            GroupsModel.admin_id != user_id
        ).all()

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

        if not group:
            abort(404, message="Group does not exist")

        return group
    
    @jwt_required()
    @blp.arguments(CreateGroupsSchema)
    @blp.response(201, CreateGroupsSchema)
    def post(self, group_data):
        
        user_id = get_jwt_identity()

        user = UserModel.query.get_or_404(user_id)

        try:
            newgroup = GroupsModel(**group_data, admin_id=user_id)
            newgroup.user.append(user)
            db.session.add(newgroup)
            db.session.commit()
        except IntegrityError:
            abort(409, message="A group with this name already exists")

        return newgroup

    # Anyone who has group id can join the group
    @jwt_required()
    @blp.arguments(JoinGroupsSchema)
    @blp.response(200, JoinGroupsSchema)
    def put(self, group_data):

        user_id = get_jwt_identity()

        group = GroupsModel.query.get_or_404(group_data["id"])
        user = UserModel.query.get_or_404(user_id)

        users_groups = UsersGroups.query.filter(
            UsersGroups.user_id == user.id,
            UsersGroups.group_id == group.id
        ).first()

        if users_groups:
            abort(409, message="The user is already in the group")

        group.user.append(user)
        db.session.add(group)
        db.session.commit()

        return group

    # Admin can delete a group
    @jwt_required(fresh=True)
    @blp.arguments(DeleteGroupSchema)
    @blp.response(201)
    def delete(self, group_data):

        user_id = get_jwt_identity()

        group = GroupsModel.query.get_or_404(group_data["id"])

        if group and group.admin_id == user_id:
            db.session.delete(group)
            db.session.commit()
            return {"message": "Group deleted."}
        elif group.admin_id != user_id:
            abort(401, message="Only admin can delete group")
        else:
            abort(404, message="Group does not exist. It may have already been removed")
    

@blp.route("/groups_users")
class Group(MethodView):

    # Admin can delete group users
    @jwt_required()
    @blp.arguments(DeleteUserFromGroup)
    def delete(self, group_data):
        
        is_admin = get_jwt_identity()

        group = GroupsModel.query.filter(
            GroupsModel.id == group_data["id"]
        ).first()

        users_groups = UsersGroups.query.filter(
            UsersGroups.user_id == group_data["user_id"] and
            UsersGroups.group_id == group_data["id"]
        ).first()

        if group.admin_id == is_admin:
            db.session.delete(users_groups)
            db.session.commit()
            return {"message": "User deleted from group"}
        
        else:
            return {"message": "None"}
