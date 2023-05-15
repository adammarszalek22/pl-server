from db import db

class BlocklistModel(db.Model):
    __tablename__ = "blocklist"

    jwt = db.Column(db.String, primary_key=True)

    def __init__(self, jwt):
        self.jwt = jwt