#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python utility/generate_key.py
python utility/encrypt_secrets.py
