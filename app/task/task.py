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



def my_job():
    str_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = 'my_job:  process id {}, thread id {}, time {}'.format(
        os.getpid(), threading.get_ident(), str_now)
    #
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        gunicorn_logger.info(message)
    print(message)


# 一个函数，用来做定时任务的任务。
def job_1(a, b):
    str_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = 'job_1: process id {}, thread id {}, time {}, {} + {}'.format(
        os.getpid(), threading.get_ident(), str_now, str(a), str(b))
    #
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        gunicorn_logger.info(message)
    print(message)




