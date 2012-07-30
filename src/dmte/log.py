# encoding=utf8
'''
Логирование.
@author: Mic, 2012
'''

from logging import Formatter, StreamHandler, getLogger, DEBUG

formatter = Formatter('%(asctime)s [%(levelname)s] %(message)s')

handler = StreamHandler()
handler.setFormatter(formatter)

logger = getLogger()
logger.addHandler(handler)
logger.setLevel(DEBUG)
