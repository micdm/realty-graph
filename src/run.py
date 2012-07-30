# coding=utf8

from lxml import etree

from dmte.loaders import get_page_content
from dmte.log import logger
from dmte.parsers import AdvertListParser
from dmte.processors import AdvertProcessor

def save_advert(advert):
    processor = AdvertProcessor()
    stored = processor.get_by_external_id(advert.external_id)
    if stored is not None:
        logger.debug('advert with external id %s found', advert.external_id)
        advert.id = stored.id
    processor.save(advert)

def parse_adverts(url):
    logger.debug('parsing advert on %s', url)
    content = get_page_content(url)
    root_node = etree.fromstring(content, parser=etree.HTMLParser())
    parser = AdvertListParser()
    for advert in parser.parse(root_node):
        logger.debug('new advert %s found', str(advert))
        save_advert(advert)

parse_adverts('http://www.tomsk.ru09.ru/realty?listview=1&type=1&otype=1')
