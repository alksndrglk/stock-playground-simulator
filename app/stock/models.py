from dataclasses import dataclass
from typing import Dict, List, Optional

from app.store.database.gino import db


@dataclass
class Game:
    users: List[User]
    chat_id: int
    state: dict


class GameModel(db.Model):
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), server_default="now()")
    chat_id = db.Column(db.Integer, nullable=False)
    round_info = db.Column(db.JSONB, server_default="{}")
    round_number = db.IntegerProperty(prop_name="round_info")
    finished_bidding = db.ArrayProperty(prop_name="round_info")
    state = db.Column(db.JSONB, server_default="{}")

    def __init__(self, **kw):
        super().__init__(**kw)
        self._users = []

    @property
    def users(self):
        return self._users

    @users.setter
    def add_users(self, user):
        self._users.append(user)

    def to_dct(self):
        return Game(users=self.users, chat_id=self.chat_id, state=self.state)


@dataclass
class User:
    pass

class UserModel(db.Model):
    pass

@dataclass
class Stock:
    pass

class StockModel(db.Model):
    pass

@dataclass
class StockMarketEvent:
    pass

class StockMarketEventModel(db.Model):
    pass


@dataclass
class BrokerageAccount:
    pass

class BrokerageAccountModel(db.Model):
    pass
