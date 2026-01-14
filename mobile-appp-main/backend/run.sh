#!/bin/bash
# Run script for development

export FLASK_APP=app/main.py
export FLASK_ENV=development

python app/main.py

