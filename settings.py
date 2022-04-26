# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_URI = os.environ.get("DB_URI")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")