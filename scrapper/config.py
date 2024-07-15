import os
import json


PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')

if not os.path.exists(CONFIG_PATH):
    raise Exception("No configuration file found")

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)


DEBUG = config.get("DEBUG", False)

REDSHIFT_HOST = config.get("REDSHIFT_HOST")
REDSHIFT_PORT = config.get("REDSHIFT_PORT")
REDSHIFT_USER = config.get("REDSHIFT_USER")
REDSHIFT_PASSWORD = config.get("REDSHIFT_PASSWORD")
REDSHIFT_DB_NAME = config.get("REDSHIFT_DB_NAME")

PROXY_LIST = config.get("PROXY_LIST", [])