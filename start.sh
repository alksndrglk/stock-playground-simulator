#!/bin/bash
envsubst <config/prod_config.yml> config/prod_config.yml

alembic upgrade head
python main.py
