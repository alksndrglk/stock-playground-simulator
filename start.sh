#!/bin/bash
cat config/prod_config.yml | envstubs > config/config.yml

alembic upgrade head
python main.py
