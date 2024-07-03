import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = eval(os.getenv("DEBUG"))

# HOST = os.getenv("DB_HOST")
# PORT = os.getenv("DB_PORT")
# USERNAME = os.getenv("DB_USERNAME")
# PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")

REDSHIFT_HOST = os.getenv("REDSHIFT_HOST")
REDSHIFT_PORT = os.getenv("REDSHIFT_PORT")
REDSHIFT_USER = os.getenv("REDSHIFT_USER")
REDSHIFT_PASSWORD = os.getenv("REDSHIFT_PASSWORD")
REDSHIFT_DB_NAME = os.getenv("REDSHIFT_DB_NAME")

PROXY_LIST = os.getenv("PROXY_LIST").split(",")