#!/bin/bash
cat config/prod_config.yml | envsubst > config/config.yaml

alembic upgrade head
python main.py
