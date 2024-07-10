import ast
import os
from dotenv import load_dotenv

PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__))

is_loaded = load_dotenv(dotenv_path=f"{PROJECT_ROOT}/.env")

if not is_loaded:
    raise Exception("No environment varibale set")


DEBUG = ast.literal_eval(os.getenv("DEBUG", "False"))

REDSHIFT_HOST = os.getenv("REDSHIFT_HOST")
REDSHIFT_PORT = os.getenv("REDSHIFT_PORT")
REDSHIFT_USER = os.getenv("REDSHIFT_USER")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD")
REDSHIFT_DB_NAME = os.getenv("REDSHIFT_DB_NAME")

PROXY_LIST = os.getenv("PROXY_LIST", "").split(",")