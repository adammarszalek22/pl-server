from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import current_app
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel, BlocklistModel
from schemas import PlainUserSchema, UserSchema, AllUserSchema, UsernameSchema, UserSchemaByPos, RegisterSchema, FirstTenSchema


blp = Blueprint('Users', 'users', description='Operations on users')


@blp.route('/register')
class UserRegister(MethodView):

    @blp.arguments(RegisterSchema)
    @blp.response(201)
    def post(self, user_data):

        another_user = UserModel.query.filter(
            UserModel.username == user_data['username']
            ).first()

        if another_user:
            abort(409, message='A user with that username already exists.')
        
        if user_data["password"] != user_data["password2"]:
            abort(401, message="Passwords do not match")
        
        user = UserModel(
            username = user_data['username'],
            password = pbkdf2_sha256.hash(user_data['password']),
            points = 0,
            position = 10000,
            three_pointers = 0,
            one_pointers = 0
        )
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        return {
                'message': 'User created successfully.',
                'access_token': access_token,
                'refresh_token': refresh_token, 
                'user_id': user.id
                }


@blp.route('/login')
class UserLogin(MethodView):

    @blp.arguments(PlainUserSchema)
    @blp.response(200)
    def post(self, user_data):

        user = UserModel.query.filter(
            UserModel.username == user_data['username']
        ).first()

        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token, 
                'user_id': user.id
                }
        elif not user:
            abort(401, message='User not found')
        else:
            abort(401, message='Wrong password')


@blp.route('/get_all')
class GetUsers(MethodView):

    # Anyone who is logged in can view all users info (points, etc. NO PASSWORD)
    @jwt_required()
    @blp.response(200, AllUserSchema(many=True))
    def get(self):

        users = UserModel.query.all()

        return users

        
@blp.route('/refresh')
class TokenRefresh(MethodView):

    # Getting a non-fresh token (do not let delete account with non-fresh token)
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

        user = UserModel.query.get_or_404(user_id)

        return user

@blp.route('/user_pos')
class UserPosition(MethodView):

    @blp.arguments(UserSchemaByPos)
    @blp.response(200, UserSchemaByPos)
    @jwt_required()
    def get(self, data):

        user = UserModel.query.filter(
            UserModel.position == data["position"]
        ).first()

        return user


@blp.route('/first-ten')
class UserPosition(MethodView):

    @blp.response(200, FirstTenSchema(many=True))
    @jwt_required()
    def get(self):

        first10 = []
        for i in range(1, 11):
            user = UserModel.query.filter(
                UserModel.position == i
            ).first()
            first10.append(user)

        return first10


# New route, the one above to be deleted
@blp.route('/users')
class UserPosition(MethodView):

    @blp.response(200, FirstTenSchema(many=True))
    @jwt_required()
    def get(self):
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        sort_by = request.args.get('sort_by', 'position')
        sort_order = request.args.get('sort_order', 'asc')
        
        if sort_order == 'desc':
            query = UserModel.query.order_by(getattr(UserModel, sort_by).desc())
        else:
            query = UserModel.query.order_by(getattr(UserModel, sort_by))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        users = pagination.items

        return users
    

@blp.route('/user')
class User(MethodView):

    @blp.arguments(UsernameSchema)
    @blp.response(200, UsernameSchema)
    @jwt_required()
    def get(self, user_data):

        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        return user

@blp.route('/delete')
class UserDelete(MethodView):

    @jwt_required(fresh=True)
    def delete(self):
        
        user_id = get_jwt_identity()
        user = UserModel.query.get_or_404(user_id)
        
        # Delete all bets first
        for bet in user.bets:
            db.session.delete(bet)
            db.session.commit()

        db.session.delete(user)
        db.session.commit()

        return {'message': 'User deleted.'}
    