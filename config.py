# -*- coding: utf-8 -*-
# Description: 应用配置文件
# Created: shaoluyu 2019/10/29
# Modified: shaoluyu 2019/10/29

import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """默认配置
    """
    # 应用参数
    APP_NAME = 'models-gc-goods-allocation'
    SERVER_PORT = 9238
    #
    FLATPAGES_AUTO_RELOAD = True
    FLATPAGES_EXTENSION = '.md'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'can you guess it'
    DEBUG = True

    # sqlalchemy两个主要配置
    # 关闭数据库时是否自动提交事务
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 是否追踪修改
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 是否开启任务调度器,默认不开启
    SCHEDULER_OPEN = False
    SCHEDULER_API_ENABLED = False
    # 任务调度器lock文件名称
    SCHEDULER_LOCK_FILE_NAME = 'scheduler-{}.lock'.format(APP_NAME)

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """开发环境配置
    """
    # Mysql配置，可选（不使用时可删除）
    MYSQL_HOST = '47.99.118.183'
    MYSQL_PORT = 3306
    MYSQL_USER = 'v3dev_user'
    MYSQL_PASSWD = 'V3dev!56'
    MYSQL_DB = 'db_trans_plan'
    MYSQL_CHARSET = 'utf8'
    # sqlalchemy ORM底层所访问数据库URI，可选（不使用时可删除）
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset={}'.format(
        MYSQL_USER, MYSQL_PASSWD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB, MYSQL_CHARSET)

    # Redis配置，可选（不使用时可删除）
    REDIS_HOST = '47.99.118.183'
    REDIS_PORT = '6379'
    REDIS_PASSWD = 'wobugaoxing'
    REDIS_MAX_CONNECTIONS = 2

    # APScheduler定时任务配置，可选（不使用时可删除）
    SCHEDULER_OPEN = False
    SCHEDULER_API_ENABLED = True
    JOBS = [
        # {
        #     # 单次立即任务。有不执行的可能！
        #     'id': 'job_1_0',
        #     'func': 'app.task.task:job_1',
        #     'args': (1, 2)
        # },
        # {
        #   # 单次定时任务
        #     'id': 'job_1_01',
        #     'func': 'app.task.task:job_1',
        #     'args': (1, 2),
        #     'trigger': 'date',
        #     'run_date': datetime.datetime.now() + datetime.timedelta(seconds=20)
        # },
        # {
        #       # 周期定时任务
        #     'id': 'redis_task',
        #     'func': 'app.task.task:Task1.redis_task',
        #     'args': None,
        #     'trigger': 'interval',
        #     'seconds': 30
        # },
        # {
        #     # cron定时任务
        #     'id': 'job_1',
        #     'func': 'app.task.task:job_1',
        #     'args': (1, 2),
        #     'trigger': 'cron',
        #     # 'hour': '17',
        #     'minute': '2-59/5'
        # }
    ]

    # Celery配置，可选（不使用时可删除）
    # CELERY_BROKER_URL = 'redis://:wobugaoxing@47.99.118.183:6379/0'
    # CELERY_RESULT_BACKEND = 'redis://:wobugaoxing@47.99.118.183:6379/0'
    # # 导入任务所在的模块
    # CELERY_IMPORTS = ('app.task.celery_task', 'app.task.celery_task2')
    # # 设置定时任务
    # from datetime import timedelta
    # from celery.schedules import crontab
    # CELERY_TIMEZONE = 'Asia/Shanghai'  # 指定时区，不指定默认为 'UTC'
    # CELERYBEAT_SCHEDULE = {
    #     'add-every-30-seconds': {
    #         'task': 'app.task.celery_task.add_together',
    #         'schedule': timedelta(seconds=30),  # 每30秒执行一次
    #         'args': (5, 8)  # 任务函数参数
    #     },
    #     'print-at-some-time': {
    #         'task': 'app.task.celery_task.print_hello',
    #         'schedule': crontab(minute='0-59/2'),
    #         'args': None
    #     },
    #     'multiply-every-60-seconds': {
    #         'task': 'app.task.celery_task2.multiply_together',
    #         'schedule': timedelta(seconds=60),  # 每30秒执行一次
    #         'args': (3, 4)  # 任务函数参数
    #     },
    # }


class TestConfig(Config):
    """测试环境配置
    """


class UatConfig(Config):
    """测试环境配置
    """


class ProductionConfig(Config):
    """生产环境配置
    """


# 设置环境配置映射
config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'uat': UatConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_active_config():
    """获取当前生效的环境配置类

    :return: 当前生效的环境配置类
    """
    config_name = os.getenv('FLASK_CONFIG') or 'default'
    return config[config_name]


def get_active_config_name():
    """获取当前生效的环境配置名称

    :return: 当前生效的环境配置名称
    """
    config_name = os.getenv('FLASK_CONFIG') or 'default'
    return config_name
