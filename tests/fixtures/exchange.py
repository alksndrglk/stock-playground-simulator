import pytest

from app.stock.models import Stock, StockMarketEvent


@pytest.fixture
async def stock_1(store) -> Stock:
    stock = await store.exchange.create_stock(
        description="Desc", symbol="TEST", cost=11
    )
    yield stock


@pytest.fixture
async def stock_2(store) -> Stock:
    stock = await store.exchange.create_stock(
        description="Desc_2", symbol="TEST_2", cost=11
    )
    yield stock

@pytest.fixture
async def event_1(store) -> StockMarketEvent:
    event = await store.exchange.create_event(
        message='Test_1', diff=0.5
    )
    yield event

@pytest.fixture
async def event_2(store) -> StockMarketEvent:
    event = await store.exchange.create_event(
        message='Test_2', diff=0.2
    )
    yield event
