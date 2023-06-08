import os
import requests
import sys
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256

from models import UserModel
from db import db

load_dotenv()

def example():
    # user = UserModel(
    #         username = 'adam2',
    #         password = pbkdf2_sha256.hash('1234'),
    #         points = 0,
    #         position = 0,
    #         three_pointers = 0,
    #         one_pointers = 0
    #     )
    # db.session.add(user)
    # db.session.commit()
    print("Just seeing how this works.", file=sys.stderr)