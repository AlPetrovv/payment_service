#!/bin/bash
set -e

cd /home/app/src
exec poetry run python consumer_main.py
