import secrets

from db import db
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from flask_jwt_extended import create_refresh_token

from db import db
from models import UserModel, StoreModel, TagModel, ItemModel
from schemas import UserSchema, TagSchema, TagAndItemSchema
from utils.redis_helper import RedisClient


blp = Blueprint("Users", "users", description="Operations on users")
redis_client = RedisClient().get_redis()

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409,message="A user with that username already exists.")

        user = UserModel(
            username=user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )
        try:
            db.session.add(user)
            db.session.commit()

        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {"message": "User created successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, expires_delta=False)
            refresh_token = create_refresh_token(identity=user.id)

            # Armazene o token JWT no Redis
            redis_client.setex(f"user_token:{user.id}", 300, access_token)
            return {"access_token": access_token,
                    "refresh_token": refresh_token}

        abort(401, message="Wrong user credentials")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        return {"access_token": new_token}, 200

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        # Obtenha o ID do usuário a partir do token JWT
        current_user_id = get_jwt_identity()
        # Bloqueie o token JWT associado ao ID do usuário
        redis_client.delete(f"user_token:{current_user_id}")

        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {"message": "User deleted."}, 200
