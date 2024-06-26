#!/bin/bash

cd $(dirname $0)/../flask_app/src

# Activate the virtual environment
source ../../myenv/Scripts/activate
# Set Flaks env variables
export FLASK_APP=app.py
export FLASK_DEBUG=1 # Set 0 for production

# Run Flask
flask run &

cd ../../react_app

npm start

