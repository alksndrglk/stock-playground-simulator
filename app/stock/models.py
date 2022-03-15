from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import and_

from app.store.database.gino import db
from gino.dialects.asyncpg import JSONB

from app.store.bot.errors import SymbolNotInPortfolio, OperationIsUnavailable

# from app.store.bot.const import minus


@dataclass
class BrokerageAccount:
    id: Optional[int] = None
    user_id: int = 0
    game_id: int = 0
    points: float = 0
    portfolio: Dict[str, int] = field(default_factory=dict)

    def __str__(self) -> str:
        minus = b"\xE2\x9E\x96"
        p = "\n".join(
            [f"{k}{minus.decode()}{v}" for k, v in self.portfolio.items()]
        )
        return f"На счете: {self.points:.2f}💲\nAкции:\n{p}"

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
        db.Integer,
        db.ForeignKey("player.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id = db.Column(
        db.Integer, db.ForeignKey("game.id", ondelete="CASCADE"), nullable=False
    )
    points = db.Column(db.Float)
    portfolio = db.Column(JSONB, server_default="{}")

    def to_dct(self) -> BrokerageAccount:
        return BrokerageAccount(**self.to_dict())


@dataclass
class User:
    id: Optional[int]
    user_id: int
    user_name: str
    brokerage_account: Optional["BrokerageAccount"] = field(
        default_factory=BrokerageAccount
    )

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
    finished_at: Union[None, datetime] = None


class GameModel(db.Model):
    __tablename__ = "game"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), server_default="now()")
    chat_id = db.Column(db.Integer, nullable=False)
    round_info = db.Column(JSONB, server_default="{}")
    round_number = db.IntegerProperty(prop_name="round_info")
    finished_bidding = db.ArrayProperty(prop_name="round_info")
    state = db.Column(JSONB, server_default="{}")
    finished_at = db.Column(db.DateTime(), server_default=None)

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

    @classmethod
    async def get_or_create(cls, peer_id: int) -> "GameModel":
        game = await cls.query.where(
            and_(cls.finished_at == None, cls.chat_id == peer_id)
        ).gino.first()
        if game is None:
            return await cls.create(
                chat_id=peer_id, round_number=1, finished_bidding=[]
            )
        return game

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

    game_id = db.Column(
        db.Integer, db.ForeignKey("game.id", ondelete="CASCADE")
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("player.id", ondelete="CASCADE")
    )


def model(table):
    class Base:
        __tablename__ = table

        id = db.Column(db.Integer, primary_key=True)
        description = db.Column(db.String, nullable=False)
        cost = db.Column(db.Float, nullable=False)

    return Base


class StockModel(db.Model, model("stock")):
    symbol = db.Column(db.String, unique=True, index=True, nullable=False)

    def to_dct(self) -> Stock:
        return Stock(
            id=self.id,
            symbol=self.symbol,
            description=self.description,
            cost=self.cost,
        )


class GameStockModel(db.Model, model("stock_in_game")):
    symbol = db.Column(db.String, index=True, nullable=False)
    game_id = db.Column(
        db.Integer, db.ForeignKey("game.id", ondelete="CASCADE")
    )
    _idx1 = db.UniqueConstraint("symbol", "game_id", name="pk")

    def to_dct(self) -> Stock:
        return Stock(
            id=self.id,
            game_id=self.game_id,
            symbol=self.symbol,
            description=self.description,
            cost=self.cost,
        )

    @classmethod
    def bulk_upsert(cls, stocks: List[Stock], diff: float):
        qs = insert(cls.__table__).values(
            [
                {
                    "cost": s.cost * diff,
                    "symbol": s.symbol,
                    "game_id": s.game_id,
                    "description": s.description,
                }
                for s in stocks
            ]
        )

        return (
            qs.on_conflict_do_update(
                index_elements=[cls.game_id, cls.symbol],
                set_={"cost": qs.excluded["cost"]},
            )
            .returning(GameStockModel.__table__)
            .gino.all()
        )


@dataclass
class StockMarketEvent:
    id: Optional[int]
    message: str
    diff: float

    def __str__(self) -> str:
        return f"Новый день торгов открылся с новости:\n{self.message}\n\n"


class StockMarketEventModel(db.Model):
    __tablename__ = "market_events"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String, unique=True, nullable=False)
    diff = db.Column(db.Float, nullable=False)

    def to_dct(self) -> StockMarketEvent:
        return StockMarketEvent(**self.to_dict())
