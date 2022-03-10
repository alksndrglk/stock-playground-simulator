import asyncio
from typing import Any, Optional

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response

from app.store.database.gino import db


def periodic(time):
    def scheduler(fcn):
        async def wrapper(*args, **kwargs):
            while True:
                await asyncio.sleep(10)
                asyncio.create_task(fcn(*args, **kwargs))
        return wrapper
    return scheduler

def secure_game_creation(func):
    async def wrapper(*ag, **kw):
        async with db.transaction():
            return await func(*ag, **kw)

    return wrapper


def json_response(data: Any = None, status: str = "ok") -> Response:
    if data is None:
        data = {}
    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )


def error_json_response(
    http_status: int,
    status: str = "error",
    message: Optional[str] = None,
    data: Optional[dict] = None,
):
    if data is None:
        data = {}
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "message": str(message),
            "data": data,
        },
    )
