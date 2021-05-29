# coding: UTF-8
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET')
