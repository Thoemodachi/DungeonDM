#!/bin/bash
# local.sh - starts the backend and frontend using docker-compose

# Exit immediately if a command fails
set -e

# Build and start containers
docker-compose up --build
