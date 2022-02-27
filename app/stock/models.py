from dataclasses import dataclass
from typing import Optional

from app.store.database.gino import db


@dataclass
class Game:
    pass


class GameModel(db.Model):
    pass


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
