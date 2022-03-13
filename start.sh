#!/bin/bash
envsubst <config/prod_config.yaml> config/prod_config.yaml

alembic upgrade head
python main.py
