#!/bin/bash
set -e

cd /home/app/src
exec poetry run python relay_main.py
