#!/bin/bash
cat config/prod_config.yml | envsubst > config/config.yml

alembic upgrade head
python main.py
