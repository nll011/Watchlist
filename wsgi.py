# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 11:51:39 2022

@author: neo
"""
import os

from dotenv import load_dotenv

dotenv_path=os.path.join(os.path.dirname(__file__),'.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from watchlist import app