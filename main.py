import os
import pathlib

from app.web.app import setup_app
from aiohttp.web import run_app

BASE_DIR = pathlib.Path(__file__).parent.parent

if os.environ.get("CONFIGPATH"):
    config_path = BASE_DIR / os.environ["CONFIGPATH"]
else:
    config_path = BASE_DIR / "config" / "config.yml"

if __name__ == "__main__":
    run_app(
        setup_app(
            config_path=config_path
        )
    )
