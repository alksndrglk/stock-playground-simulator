from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import and_

from app.store.database.gino import db
from gino.dialects.asyncpg import JSONB

from app.store.bot.errors import SymbolNotInPortfolio, OperationIsUnavailable


@dataclass
class User:
    id: Optional[int]
    user_id: int
    user_name: str
    brokerage_account: Optional["BrokerageAccount"] = field(default_factory=dict)

    def __str__(self) -> str:
        return str(self.brokerage_account)


class UserModel(db.Model):
    __tablename__ = "player"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(), server_default="now()")

    def __init__(self, **kw):
        super().__init__(**kw)
        self._games = set()
        self._portfolio = None

    @property
    def games(self):
        return self._games

    @property
    def portfolio(self):
        return self._portfolio

    @portfolio.setter
    def portfolio(self, value: "BrokerageAccountModel"):
        self._portfolio = value

    def to_dct(self) -> User:
        return User(
            id=self.id,
            user_id=self.user_id,
            user_name=self.user_name,
            brokerage_account=self._portfolio.to_dct(),
        )


@dataclass
class Stock:
    symbol: str
    description: str
    cost: float
    game_id: Optional[int] = None
    id: Optional[int] = None

    def __str__(self) -> str:
        return f"{self.description} {self.symbol} {self.cost:.2f}"


@dataclass
class Game:
    id: Optional[int]
    users: Dict[int, User]
    chat_id: int
    state: dict
    round_info: dict
    stocks: Dict[str, Stock]


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
        self._users = {}
        self._stocks_in_game = {}

    @property
    def stocks(self):
        return self._stocks_in_game

    @stocks.setter
    def add_stocks(self, stock: "GameStockModel"):
        self._stocks_in_game[stock.symbol] = stock.to_dct()

    @property
    def users(self):
        return self._users

    @users.setter
    def add_users(self, user: UserModel):
        self._users[user.user_id] = user.to_dct()
        user.games.add(self.id)

    def to_dct(self) -> Game:
        return Game(
            id=self.id,
            users=self.users,
            chat_id=self.chat_id,
            state=self.state,
            stocks=self.stocks,
            round_info=self.round_info,
        )


class GameXUser(db.Model):
    __tablename__ = "games_x_users"

    game_id = db.Column(db.Integer, db.ForeignKey("game.id", ondelete="CASCADE"))
    user_id = db.Column(db.Integer, db.ForeignKey("player.id", ondelete="CASCADE"))


def model(table):
    class Base:
        __tablename__ = table

        id = db.Column(db.Integer, primary_key=True)
        symbol = db.Column(db.String, unique=True, index=True, nullable=False)
        description = db.Column(db.String, nullable=False)
        cost = db.Column(db.Float, nullable=False)

    return Base


class StockModel(db.Model, model("stock")):
    def to_dct(self) -> Stock:
        return Stock(symbol=self.symbol, description=self.description, cost=self.cost)


class GameStockModel(db.Model, model("stock_in_game")):
    game_id = db.Column(db.Integer, db.ForeignKey("game.id", ondelete="CASCADE"))

    def to_dct(self) -> Stock:
        return Stock(
            id=self.id,
            game_id=self.game_id,
            symbol=self.symbol,
            description=self.description,
            cost=self.cost,
        )

    @classmethod
    def bulk_upsert(cls, stocks, diff, game_id):
        qs = insert(cls.__table__).values(
            [
                {
                    "cost": s.cost * (100 + diff) / 100,
                    "symbol": s.symbol,
                    "game_id": s.game_id,
                    "description": s.description,
                }
                for s in stocks
            ]
        )

        return (
            qs.on_conflict_do_update(
                index_elements=[cls.symbol],
                set_={
                    "cost": qs.excluded["cost"]
                },  # or even qs.excluded['some_column']
            )
            .returning(GameStockModel.__table__)
            .gino.all()
        )


@dataclass
class StockMarketEvent:
    id: Optional[int]
    message: str
    diff: int

    def __str__(self) -> str:
        return f"Новый день торгов открылся с новости:\n{self.message}\n\n"


class StockMarketEventModel(db.Model):
    __tablename__ = "market_events"

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

    def __str__(self) -> str:
        return f"На счете: {self.points}$, акции: {self.portfolio}"

    def sell(
        self, symbol: str, quantity: int, cost: float
    ) -> Optional["BrokerageAccount"]:
        if symbol not in self.portfolio:
            raise SymbolNotInPortfolio
        if quantity > self.portfolio[symbol]:
            raise OperationIsUnavailable

        self.portfolio[symbol] -= quantity
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        self.points += quantity * cost
        return self

    def buy(
        self, symbol: str, quantity: int, cost: float
    ) -> Optional["BrokerageAccount"]:
        if (quantity * cost) > self.points:
            raise OperationIsUnavailable
        self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity
        self.points -= quantity * cost
        return self


class BrokerageAccountModel(db.Model):
    __tablename__ = "brokerage_accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("player.id", ondelete="CASCADE"), nullable=False
    )
    game_id = db.Column(
        db.Integer, db.ForeignKey("game.id", ondelete="CASCADE"), nullable=False
    )
    points = db.Column(db.Float)
    portfolio = db.Column(JSONB, server_default="{}")

    def to_dct(self) -> BrokerageAccount:
        return BrokerageAccount(**self.to_dict())
