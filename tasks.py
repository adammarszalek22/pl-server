import os
import requests
import sys
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256

from models import UserModel
from db import db

import redis
from datetime import datetime
from rq_scheduler import Scheduler

load_dotenv()

def example():
    print("Successfully logged in", file=sys.stderr)

def example1():
    pass
