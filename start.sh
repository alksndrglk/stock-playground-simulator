#!/bin/bash
. .env
envsubst < config/prod_config.yml > config/config.yaml

alembic upgrade head
python main.py
