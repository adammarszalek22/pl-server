from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel
from schemas import PlainUserSchema, UserUpdateSchema, DeleteUserSchema

blp = Blueprint('Users-admin', 'users', description='Admin operations on users')


@blp.route('/admin/login')
class UserLogin(MethodView):

    @blp.arguments(PlainUserSchema)
    @blp.response(200)
    def post(self, user_data):

        if user_data["username"] != "adam1234":
            abort(401, message="Invalid credentials.")

        user = UserModel.query.filter(
            UserModel.username == user_data['username']
        ).first()

        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.username, fresh=True)
            refresh_token = create_refresh_token(identity=user.username)
            current_app.queue.enqueue(example)
            return {'access_token': access_token,
                    'refresh_token': refresh_token, 
                    'user_id': user.id}
        elif not user:
            abort(401, message='User not found')
        else:
            abort(401, message='Wrong password')

@blp.route('/admin/update')
class UpdateInfo(MethodView):

    @jwt_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserUpdateSchema)
    def put(self, user_data):

        admin = get_jwt()

        user = UserModel.query.get_or_404(user_data["user_id"])

        if user and admin["is_admin"] == True:
            user.points = user_data["points"]
            user.three_pointers = user_data["three_pointers"]
            user.one_pointers = user_data["one_pointers"]

            db.session.add(user)
            db.session.commit()

            return user

@blp.route('/admin/delete')
class DeleteUser(MethodView):

    @jwt_required()
    @blp.arguments(DeleteUserSchema)
    def delete(self, data):
        admin = get_jwt()

        if not admin["is_admin"]:
            abort(401, message="Unauthorized")

        user = UserModel.query.get_or_404(data["user_id"])
        
        # Delete all bets first
        for bet in user.bets:
            db.session.delete(bet)
            db.session.commit()

        db.session.delete(user)
        db.session.commit()

        return {'message': 'User deleted.'}