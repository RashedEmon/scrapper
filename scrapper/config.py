import os
import json
import pkg_resources
import subprocess

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

def load_requirements(resource_name):
    resource_package = __name__
    req_file = pkg_resources.resource_string(resource_package, resource_name)
    requirements = []
    for line in req_file.decode().split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)
    return requirements

requirements = load_requirements(resource_name='requirements.txt')

for lib in requirements:
    command = ["pip", "install", lib]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except Exception as err:
        print(err)

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