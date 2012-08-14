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
    Возвращает, новое ли объявление.
    @param advert: Advert
    @return: bool
    '''
    processor = AdvertProcessor()
    stored = processor.get_by_external_id(advert.external_id)
    if stored is not None:
        logger.debug('advert with external id %s found', advert.external_id)
        advert.id = stored.id
    processor.save(advert)
    logger.debug('advert with external id %s saved', advert.external_id)
    return stored is None

def save_adverts(adverts):
    '''
    Сохраняет объявления.
    Возвращает количество новых.
    @param adverts: list
    @return: int
    '''
    count = 0
    for advert in adverts:
        if save_advert(advert):
            count += 1
    return count

def parse_page(url):
    '''
    Разбирает страницу на объявления.
    Возвращает список найденных объявлений и адрес следующей страницы.
    @param url: str
    @return: list, str
    '''
    logger.debug('parsing adverts on %s', url)
    content = get_page_content(url)
    root_node = etree.fromstring(content, parser=etree.HTMLParser())
    parser = AdvertListParser()
    return parser.parse_adverts(root_node), parser.parse_next_page_address(root_node)

def parse_all(new_only=False):
    '''
    Разбирает все страницы.
    @param new_only: bool
    '''
    if new_only:
        logger.info('parsing new adverts only')
    else:
        logger.info('parsing all adverts')
    next_url = '/realty/?type=1&otype=1&listview=1&perpage=200'
    total_count = 0
    while True:
        adverts, next_url = parse_page('http://www.tomsk.ru09.ru%s'%next_url)
        count = save_adverts(adverts)
        logger.debug('%s new adverts found on page', count)
        total_count += count
        if new_only and count == 0:
            logger.info('no new adverts found on page, stopping')
            break
        if next_url is None:
            logger.info('last page reached, stopping')
            break
        sleep(1)
    logger.info('%s new adverts found', total_count)

new_only = len(sys.argv) > 1 and sys.argv[1] == 'new'
parse_all(new_only)
