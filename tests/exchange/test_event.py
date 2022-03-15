from app.stock.models import StockMarketEvent, StockMarketEventModel
from tests.utils import ok_response
from tests.exchange import event2dict
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from asyncpg.exceptions import UniqueViolationError


class TestEventStore:
    async def test_table_exists(self, cli):
        await check_empty_table_exists(cli, "market_events")

    async def test_create_event(self, cli, store: Store):
        event_message = "Down"
        event_diff = 0.9
        event = await store.exchange.create_event(event_message, event_diff)
        assert type(event) is StockMarketEvent

        db = cli.app.database.db
        events = await StockMarketEventModel.query.gino.all()
        assert len(events) == 1
        assert event.message == event_message and event.id == 1

    async def test_create_event_unique_message_constraint(
        self, cli, store: Store, event_1: StockMarketEvent
    ):
        with pytest.raises(UniqueViolationError):
            await store.exchange.create_event(event_1.message, event_1.diff)


class TestEventAddView:
    async def test_unauthorized(self, cli):
        resp = await cli.post(
            "/exchange.add_event",
            json={
                "message": "TEST",
                "diff": 0.99,
            },
        )
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_success(self, store: Store, authed_cli):
        resp = await authed_cli.post(
            "/exchange.add_event",
            json={
                "message": "TEST",
                "diff": 0.99,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data=event2dict(
                StockMarketEvent(
                    id=data["data"]["id"],
                    message="TEST",
                    diff=0.99,
                )
            ),
        )

        events = await store.exchange.list_events()
        assert len(events) == 1

    async def test_missing(self, authed_cli):
        resp = await authed_cli.post("/exchange.add_event", json={})
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["message"][0] == "Missing data for required field."
        assert data["data"]["diff"][0] == "Missing data for required field."

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.get("/exchange.add_event", json={})
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"

    async def test_conflict(self, authed_cli, event_1):
        resp = await authed_cli.post(
            "/exchange.add_event",
            json={
                "message": event_1.message,
                "diff": event_1.diff,
            },
        )
        assert resp.status == 409
        data = await resp.json()
        assert data["status"] == "conflict"


class TestEventList:
    async def test_unauthorized(self, cli):
        resp = await cli.get("/exchange.list_events")
        assert resp.status == 401
        data = await resp.json()
        assert data["status"] == "unauthorized"

    async def test_empty(self, authed_cli):
        resp = await authed_cli.get("/exchange.list_events")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"events": []})

    async def test_one(self, authed_cli, event_1):
        resp = await authed_cli.get("/exchange.list_events")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(data={"events": [event2dict(event_1)]})

    async def test_several(self, authed_cli, event_1, event_2):
        resp = await authed_cli.get("/exchange.list_events")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={"events": [event2dict(event_1), event2dict(event_2)]}
        )

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.post("/exchange.list_events")
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"


class TestIntegration:
    async def test_success(self, authed_cli):
        resp = await authed_cli.post(
            "/exchange.add_event",
            json={
                "message": "TEST",
                "diff": 0.99,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        event_id = data["data"]["id"]

        resp = await authed_cli.get("/exchange.list_events")
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            data={
                "events": [
                    event2dict(
                        StockMarketEvent(
                            id=event_id,
                            message="TEST",
                            diff=0.99,
                        )
                    )
                ]
            }
        )
