import os
import json
import pkg_resources


def get_package_root():
    package_root = pkg_resources.resource_filename(__name__, '')
    return package_root

def load_json_resource(resource_name):
    resource_package = __name__
    json_data = pkg_resources.resource_string(resource_package, resource_name)
    config = {}
    try:
        config = json.loads(json_data)
    except Exception as err:
        print("Error while reading config file")
    return config
    

config = load_json_resource(resource_name='config.json')

DEBUG = config.get("DEBUG", False)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if not DEBUG:
    PROJECT_ROOT=get_package_root()

REDSHIFT_HOST = config.get("REDSHIFT_HOST")
REDSHIFT_PORT = config.get("REDSHIFT_PORT")
REDSHIFT_USER = config.get("REDSHIFT_USER")
REDSHIFT_PASSWORD = config.get("REDSHIFT_PASSWORD")
REDSHIFT_DB_NAME = config.get("REDSHIFT_DB_NAME")

PROXY_LIST = config.get("PROXY_LIST", [])