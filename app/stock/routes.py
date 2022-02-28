import typing

from app.stock.views import(
    StockAddView,
    StockListView,
    EventAddView,
    EventListView,
    GameStatisticView,
)

from typing.TYPE_CHECKING:
    from app.web.app import Application

def setup_routes(app: "Application"):
    app.router.add_view('/exchange.add_stock', StockAddView)
    app.router.add_view('/exchange.list_stocks', StockListView)
    app.router.add_view('/exchange.games_stat', GameStatisticView)
    app.router.add_view('/exchange.add_event', EventAddView)
    app.router.add_view('/exchange.list_events', EventListView)
