# -*- coding: utf-8 -*-
# Description: 创建Celery应用
# Created: shaoluyu 2019/10/25
# Modified: shaoluyu 2019/10/25;

from app.task.make_celery import make_celery

# 创建celery应用
celery = make_celery(flask_app=None)