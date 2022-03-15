from app.stock.models import Stock, StockModel
from tests.utils import ok_response
from tests.exchange import stock2dict
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError


class TestStockStore:
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "stock")

    async def test_create_stock(self, cli, store: Store):
        stock_symbol = "AAPL"
        stock_description = "Apple Inc."
        stock_cost = 15.88
        stock = await store.exchange.create_stock(
            stock_symbol, stock_description, stock_cost
        )
        assert type(stock) is Stock

        db = cli.app.database.db
        stocks = await StockModel.query.gino.all()
        assert len(stocks) == 1
        assert stock.symbol == stock_symbol and stock.id == 1

    async def test_create_stock_unique_symbol_constraint(
        self, cli, store: Store, stock_1: Stock
    ):
        with pytest.raises(UniqueViolationError):
            await store.exchange.create_stock(
                stock_1.symbol, stock_1.description, stock_1.cost
            )


class TestStockAddView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/exchange.add_stock",
            json={
                "symbol": "TEST",
                "description": "Test description",
                "cost": 12.99,
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, store: Store, authed_cli):
        resp = await authed_cli.post(
            "/exchange.add_stock",
            json={
                "symbol": "TEST",
                "description": "Test description",
                "cost": 12.99,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data=stock2dict(
                Stock(
                    id=data["data"]["id"],
                    symbol="TEST",
                    description="Test description",
                    cost=12.99,
                )
            ),
        )

        stocks = await store.exchange.list_stocks()
        assert len(stocks) == 1

    async def test_missing(self, authed_cli):
        resp = await authed_cli.post("/exchange.add_stock", json={})
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["symbol"][0] == "Missing data for required field."
        assert (
            data["data"]["description"][0] == "Missing data for required field."
        )
        assert data["data"]["cost"][0] == "Missing data for required field."

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.get("/exchange.add_stock", json={})
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"

    async def test_conflict(self, authed_cli, stock_1):
        resp = await authed_cli.post(
            "/exchange.add_stock",
            json={
                "symbol": stock_1.symbol,
                "description": stock_1.description,
                "cost": stock_1.cost,
            },
        )
        assert resp.status == 409
        data = await resp.json()
        assert data["status"] == "conflict"


class TestStockList:
    async def test_unauthorized(self, cli):
        resp = await cli.get("/exchange.list_stocks")
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_empty(self, authed_cli):
        resp = await authed_cli.get("/exchange.list_stocks")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"stocks": []})

    async def test_one(self, authed_cli, stock_1):
        resp = await authed_cli.get("/exchange.list_stocks")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"stocks": [stock2dict(stock_1)]})

    async def test_several(self, authed_cli, stock_1, stock_2):
        resp = await authed_cli.get("/exchange.list_stocks")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={"stocks": [stock2dict(stock_1), stock2dict(stock_2)]}
        )

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.post("/exchange.list_stocks")
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"


class TestIntegration:
    async def test_success(self, authed_cli):
        resp = await authed_cli.post(
            "/exchange.add_stock",
            json={
                "symbol": "TEST",
                "description": "Test description",
                "cost": 12.99,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        stock_id = data["data"]["id"]

        resp = await authed_cli.get("/exchange.list_stocks")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "stocks": [
                    stock2dict(
                        Stock(
                            id=stock_id,
                            symbol="TEST",
                            description="Test description",
                            cost=12.99,
                        )
                    )
                ]
            }
        )
