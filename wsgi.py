# coding: utf-8

import os

import leancloud
from wsgiref import simple_server
from app import application

APP_ID = os.environ['LC_APP_ID']
MASTER_KEY = os.environ['LC_APP_MASTER_KEY']
PORT = int(os.environ['LC_APP_PORT'])

try:
    import config 
    APP_ID = config.leancloud_id
    MASTER_KEY = config.leancloud_key
except:
    pass

leancloud.init(APP_ID, master_key=MASTER_KEY)

from leancloud import Engine
engine = Engine(application)
application = engine


if __name__ == '__main__':
    # 只在本地开发环境执行的代码
    server = simple_server.make_server('localhost', PORT, application)
    server.serve_forever()


