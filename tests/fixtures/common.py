import asyncio
import os
from unittest.mock import AsyncMock
import pytest
from aiohttp.test_utils import TestClient, loop_context

from app.store import Store
from app.web.app import setup_app
from app.web.config import Config
from app.store import Database
from tests.data import *


@pytest.fixture(scope="session")
def loop():
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(scope="session")
def server():
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "config.yml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()
    app.store.vk_api = AsyncMock()

    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_shutdown.append(app.database.disconnect)

    app.on_startup.append(app.store.admins.connect)
    app.on_shutdown.append(app.store.admins.disconnect)
    return app


@pytest.fixture
def store(server) -> Store:
    return server.store


@pytest.fixture(autouse=True, scope="function")
async def clear_db(server):
    yield
    db = server.database.db
    for table in db.sorted_tables:
        await db.status(db.text(f"TRUNCATE {table.name} CASCADE"))
        try:
            row = await db.status(
                db.text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1")
            )
        except Exception:
            pass


@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture(autouse=True)
def cli(aiohttp_client, loop, server) -> TestClient:
    return loop.run_until_complete(aiohttp_client(server))


@pytest.fixture
async def authed_cli(cli, config) -> TestClient:
    await cli.post(
        "/admin.login",
        data={
            "email": config.admin.email,
            "password": config.admin.password,
        },
    )
    yield cli


@pytest.fixture
def create_mock_coro(mocker, monkeypatch):
    """Create a mock-coro pair.
    The coro can be used to patch an async method while the mock can
    be used to assert calls to the mocked out method.
    """

    def _create_mock_coro_pair(to_patch=None):
        mock = mocker.Mock()

        async def _coro(*args, **kwargs):
            return mock(*args, **kwargs)

        if to_patch:
            monkeypatch.setattr(to_patch, _coro)

        return mock, _coro

    return _create_mock_coro_pair


@pytest.fixture
def mock_queue(mocker, monkeypatch):
    queue = mocker.Mock()
    monkeypatch.setattr(asyncio, "Queue", queue)
    return queue.return_value


@pytest.fixture
def mock_get(mock_queue, create_mock_coro):
    mock_get, coro_get = create_mock_coro()
    mock_queue.get = coro_get
    return mock_get
