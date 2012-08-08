# encoding=utf8
'''
Получение исходных данных.
@author: Mic, 2012
'''

from time import sleep
import sys

from lxml import etree

from dmte.source_data.loaders import get_page_content
from dmte.log import logger
from dmte.source_data.parsers import AdvertListParser
from dmte.processors import AdvertProcessor

def save_advert(advert):
    '''
    Сохраняет объявление в БД.
    Возвращает True, если объявление новое.
    @param advert: Advert
    @return: bool
    '''
    processor = AdvertProcessor()
    stored = processor.get_by_external_id(advert.external_id)
    if stored is not None:
        logger.debug('advert with external id %s found', advert.external_id)
        advert.id = stored.id
    processor.save(advert)

def parse_page(url, new_only):
    '''
    Разбирает страницу на объявления.
    Возвращает адрес следующей страницы.
    @param url: str
    @param new_only: bool
    @return: str
    '''
    logger.debug('parsing adverts on %s', url)
    content = get_page_content(url)
    root_node = etree.fromstring(content, parser=etree.HTMLParser())
    parser = AdvertListParser()
    has_new = False
    for advert in parser.parse_adverts(root_node):
        logger.debug('advert %s found', str(advert))
        if save_advert(advert):
            has_new = True
    if new_only and not has_new:
        logger.debug('no new adverts found on the page %s, stopping', url)
        return None        
    return parser.parse_next_page_address(root_node)

def parse_all(new_only=False):
    '''
    Разбирает все страницы.
    @param new_only: bool
    '''
    if new_only:
        logger.debug('parsing only new adverts')
    else:
        logger.debug('parsing all adverts')
    next_url = '/realty/?type=1&otype=1&listview=1&perpage=200'
    while next_url:
        next_url = parse_page('http://www.tomsk.ru09.ru%s'%next_url, new_only)
        sleep(1)

new_only = len(sys.argv) > 1 and sys.argv[1] == 'new'
parse_all(new_only)
