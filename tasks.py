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
    print("Just seeing how this works.", file=sys.stderr)

connection = redis.from_url(
            os.getenv("REDIS_URL")
)
scheduler = Scheduler('example', connection=connection)
#scheduler.enqueue_in(timedelta(seconds=10), example)
scheduler.schedule(
    scheduled_time=datetime.utcnow(),
    func=example,
    interval=10,
    repeat=10
    )