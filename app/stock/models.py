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
    id: int
    user_id: int
    user_name: str


class UserModel(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    user_name = db.Column(db.String)
    created_at = db.Column(db.DateTime(), server_default="now()")

    game = db.Column(db.Integer, db.ForeignKey("game.id"))

    def to_dct(self):
        return User(id=self.id, user_id=self.user_id, user_name=self.user_name)


@dataclass
class Stock:
    id: Optional[int]
    symbol: str
    description: str
    cost: float
    game_id: Optional[int]


class StockModel(db.Model):
    __tablename__ = "stock"

    id = db.Column(db.Integer, primary_key=True, index=True)
    symbol = db.Column(db.String, unique=True, index=True)
    description = db.Column(db.String, nullable=False)
    cost = db.Column(db.Float, nullable=False)

    def to_dct(self):
        return Stock(**self.to_dict())


class GameStockModel(db.Model, StockModel):
    __tablename__ = "stock_in_game"

    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))


@dataclass
class StockMarketEvent:
    id: Optional[int]
    message: str
    diff: int


class StockMarketEventModel(db.Model):
    __tablename__ = "market_event"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String, nullable=False)
    diff = db.Column(db.Integer, nullable=False)

    def to_dct(self):
        return StockMarketEvent(**self.to_dict())


@dataclass
class BrokerageAccount:
    pass

class BrokerageAccountModel(db.Model):
    pass
