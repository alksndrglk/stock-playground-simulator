import os
import pathlib

from app.web.app import setup_app
from aiohttp.web import run_app

BASE_DIR = pathlib.Path(__file__).parent.parent

if os.environ.get("CONFIGPATH"):
    config_path = BASE_DIR / os.environ["CONFIGPATH"]
else:
    config_path = BASE_DIR / "config" / "config.yaml"

ON_HEROKU = os.environ.get('ON_HEROKU')

if ON_HEROKU:
    port = int(os.environ.get('PORT', 17995))
else:
    port = 8080
if __name__ == "__main__":
    run_app(
        setup_app(
            config_path=config_path
        ), port=
    )
