import os
import redis
from rq_scheduler import Scheduler
from datetime import datetime
from tasks import example
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QUEUES = ["example", "default"]

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