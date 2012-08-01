# coding=utf8

from time import sleep

from lxml import etree

from dmte.source_data.loaders import get_page_content
from dmte.log import logger
from dmte.source_data.parsers import AdvertListParser
from dmte.processors import AdvertProcessor

def save_advert(advert):
    processor = AdvertProcessor()
    stored = processor.get_by_external_id(advert.external_id)
    if stored is not None:
        logger.debug('advert with external id %s found', advert.external_id)
        advert.id = stored.id
    processor.save(advert)

def parse_page(url):
    logger.debug('parsing adverts on %s', url)
    content = get_page_content(url)
    root_node = etree.fromstring(content, parser=etree.HTMLParser())
    parser = AdvertListParser()
    for advert in parser.parse_adverts(root_node):
        logger.debug('new advert %s found', str(advert))
        save_advert(advert)
    return parser.parse_next_page_address(root_node)

def parse_all():
    next_url = '/realty/?type=1&otype=1&listview=1&perpage=50'
    while next_url:
        next_url = parse_page('http://www.tomsk.ru09.ru%s'%next_url)
        sleep(1)

parse_all()
