#!/bin/bash
sourse .env
envsubst < config/prod_config.yml > config/config.yaml

alembic upgrade head
python main.py
