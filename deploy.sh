#!/bin/bash
set -e

APP_DIR="/var/www/vhosts/mattdev.it/api.atp-radio.mattdev.it"
RESTART_FILE="/var/www/vhosts/system/api.atp-radio.mattdev.it/restart.txt"

echo "Deploying ATP Radio API..."
cd "$APP_DIR"

echo "Fetching latest code..."
git fetch origin
git reset --hard origin/main

echo "Activating virtual env..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Restarting FastAPI..."
touch "$RESTART_FILE"

echo "Deployment complete!"
