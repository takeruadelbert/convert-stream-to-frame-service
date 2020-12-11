#!/bin/bash

export $(cat environment.env | xargs)
poetry run python src/main.py