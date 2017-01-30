#!/bin/bash

set -e

python3 /update_grafana_conf.py

exec "$@"
