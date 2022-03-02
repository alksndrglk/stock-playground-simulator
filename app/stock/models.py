from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.store.database.gino import db
from gino.dialects.asyncpg import JSONB


@dataclass
class User:
    vk_id: int
    user_name: str
    id: Optional[int] = None
    games: Optional[set] = field(default_factory=set)


class UserModel(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(), server_default="now()")

    def __init__(self):
        self._games = set()

    @property
    def games(self):
        return self._games

    def to_dct(self) -> User:
        return User(
            id=self.id,
            vk_id=self.user_id,
            user_name=self.user_name,
            games=self._games,
        )


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
    round_info = db.Column(JSONB, server_default="{}")
    round_number = db.IntegerProperty(prop_name="round_info")
    finished_bidding = db.ArrayProperty(prop_name="round_info")
    state = db.Column(JSONB, server_default="{}")

    def __init__(self, **kw):
        super().__init__(**kw)
        self._users = []

    @property
    def users(self):
        return self._users

    @users.setter
    def add_users(self, user: UserModel):
        self._users.append(user)
        user.games.add(self)

    def to_dct(self) -> Game:
        return Game(users=self.users, chat_id=self.chat_id, state=self.state)


class GameXUser(db.Model):
    __tablename__ = "games_x_users"

    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


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

    def to_dct(self) -> Stock:
        return Stock(**self.to_dict())


class GameStockModel(StockModel):
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

    def to_dct(self) -> StockMarketEvent:
        return StockMarketEvent(**self.to_dict())


@dataclass
class BrokerageAccount:
    id: Optional[int]
    user_id: int
    game_id: int
    points: float
    portfolio: Dict[str, int]


class BrokerageAccountModel(db.Model):
    __tablename__ = "brokerage_account"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    points = db.Column(db.Integer)
    portfolio = db.Column(JSONB, server_default="{}")

    def to_dct(self) -> BrokerageAccount:
        return BrokerageAccount(**self.to_dict())
