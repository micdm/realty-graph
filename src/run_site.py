# encoding=utf8
'''
Запуск сайта.
@author: Mic, 2012
'''

from dmte.conf import settings
from dmte.site.views import app

app.run(settings.HTTP_SERVER['host'], settings.HTTP_SERVER['port'], settings.DEBUG)
