from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel, BlocklistModel
from schemas import PlainUserSchema, UserSchema, UserUpdateSchema, AllUserSchema
from tasks import example

import sys


blp = Blueprint('Users', 'users', description='Operations on users')


@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data['username']).first():
            abort(409, message='A user with that username already exists.')
        
        user = UserModel(
            username = user_data['username'],
            password = pbkdf2_sha256.hash(user_data['password']),
            points = 0,
            position = 0,
            three_pointers = 0,
            one_pointers = 0
        )
        db.session.add(user)
        db.session.commit()

        return {'message': 'User created successfully.', "code": 201}



@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(PlainUserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data['username']
        ).first()

        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            print('Logged in', file=sys.stderr)
            current_app.queue.enqueue(example)
            #current_app.queue.enqueue(example)
            return {'access_token': access_token, 'refresh_token': refresh_token, 
                    'user_id': user.id}
        elif not user:
            abort(401, message='User not found')
        else:
            abort(401, message='Wrong password')

@blp.route('/update/<int:user_id>')
class UpdateInfo(MethodView):
    @jwt_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        id = get_jwt()['sub']
        user = UserModel.query.get(user_id)
        if user and user.id == id:
            user.points = user_data["points"]
            user.position = user_data["position"]
            user.three_pointers = user_data["three_pointers"]
            user.one_pointers = user_data["one_pointers"]

            db.session.add(user)
            db.session.commit()

            return user
        
        abort(401, message='Cannot update other users\' accounts')


@blp.route('/get_all')
class GetUsers(MethodView):
    @jwt_required()
    @blp.response(200, AllUserSchema(many=True))
    def get(self):
        return UserModel.query.all()

        
@blp.route('/refresh')
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}


@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        blocklist_item = BlocklistModel(jti)
        db.session.add(blocklist_item)
        db.session.commit()
        return {'message': 'Successfully logged out.'}


@blp.route('/user/<int:user_id>')
class User(MethodView):
    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self, user_id):
        id = get_jwt()["sub"]
        if user_id == id:
            user = UserModel.query.get_or_404(user_id)
            return user
        else:
            abort(401, message="Unauthorised")

    @jwt_required(fresh=True)
    def delete(self, user_id):
        id = get_jwt()['sub']
        if id == user_id:
            user = UserModel.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted.'}, 200
        else:
            return {'message': 'You cannot delete other users\' accounts'}
    