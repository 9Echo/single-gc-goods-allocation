import json
import logging
import os
import threading
from datetime import datetime

import pandas as pd
import redis
from flask import current_app

from app.main.db_pool import db_pool_trans_plan
from app.main.redis_pool import redis_pool
from app.main.services.update_stock_task_service import update_stock


def update_stock_job():
    print('update stock start!')
    update_stock()






