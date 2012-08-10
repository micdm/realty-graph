# encoding=utf8
'''
Настройки.
@author: Mic, 2012
'''

# Режим отладки:
DEBUG = False
DEBUG_LOG = DEBUG

# Настройки HTTP-сервера:
HTTP_SERVER = {
    'host': 'localhost',
    'port': 5000
}

# Настройки БД:
MONGO_DB = {
    'host': 'localhost',
    'port': 27017,
    'db_name': '',
}

try:
    from settings_local import *
except ImportError:
    pass
