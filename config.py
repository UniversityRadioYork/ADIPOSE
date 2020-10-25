"""
ADIPOSE Sequence Controller
Configuration
@author Michael Grace, October 2020
"""

# Basic Settings
DEV_MODE = False
TRACKLISTING = True

# MyRadio API
API_KEY = "API_KEY"
BASE_URL = "MY_RADIO_API"
DEV_URL = "MY_RADIO_DEV_API"

# Web Server Details (within the Docker container)
HOST = "0.0.0.0"
PORT = 3000
DEBUG = False

# Allowed IPs for calling requests and starting a new sequence each hour
REQUEST_ALLOW = "1.1.1.1"
TRIGGER_ALLOW = "172.17.0.1"
