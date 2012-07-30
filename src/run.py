# coding=utf-8

from lxml import etree

from dmte.loaders import get_page_content
from dmte.parsers import AdvertListParser
from dmte.processors import AdvertProcessor

def save_advert(advert):
    print str(advert)
    processor = AdvertProcessor()
    stored = processor.get_by_external_id(advert.external_id)
    if stored is not None:
        print 'advert %s found'%advert.external_id
        advert.id = stored.id
    processor.save(advert)

def parse_adverts(url):
    content = get_page_content(url)
    root_node = etree.fromstring(content, parser=etree.HTMLParser())
    parser = AdvertListParser()
    for advert in parser.parse(root_node):
        save_advert(advert)

parse_adverts('http://www.tomsk.ru09.ru/realty?listview=1&type=1&otype=1')
