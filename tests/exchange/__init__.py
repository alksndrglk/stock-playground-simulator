from app.stock.models import Stock, StockMarketEvent


def stock2dict(stock: Stock):
    return {
        "id": int(stock.id),
        "symbol": str(stock.symbol),
        "description": str(stock.description),
        "cost": float(stock.cost),
    }


def event2dict(event: StockMarketEvent):
    return {
        "id": int(event.id),
        "message": str(event.message),
        "diff": float(event.diff),
    }
