# -*- coding: utf-8 -*-
# Description: Celery任务示例
# Created: shaoluyu 2019/10/14
# Modified: shaoluyu 2019/10/16; shaoluyu 2019/10/25;

import time

from celery.utils.log import get_task_logger
from flask import current_app

from app.task.celery_app import celery

# 获取celery执行器的日志记录器
logger = get_task_logger('celery_worker')


@celery.task()
def add_together(a, b):
    logger.info('{} + {}'.format(a, b))
    time.sleep(5)
    return a + b


@celery.task()
def print_hello():
    logger.info('Celery Hello World! {}'.format(current_app.name))
