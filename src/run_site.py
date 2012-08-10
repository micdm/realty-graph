# encoding=utf8
'''
Запуск сайта.
@author: Mic, 2012
'''

from dmte.conf import settings
from dmte.site.views import app

app.run(debug=settings.DEBUG)
