import os
import requests
import sys
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256

from models import UserModel
from db import db

load_dotenv()

def example():
    print("Just seeing how this works.", file=sys.stderr)