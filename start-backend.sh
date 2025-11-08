#!/bin/bash
# Start the Flask backend server for local development

cd "$(dirname "$0")/backend"
python3 api.py
