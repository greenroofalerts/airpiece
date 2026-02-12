#!/bin/bash
cd ~/airpiece
export $(cat .env | xargs)
python3 dev/airpiece_mac.py
