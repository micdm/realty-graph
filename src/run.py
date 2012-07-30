# coding=utf-8

from lxml import etree

from dmte.loaders import get_page_content
from dmte.parsers import AdvertListParser

content = get_page_content('http://www.tomsk.ru09.ru/realty?listview=1&type=1&otype=1')
root_node = etree.fromstring(content, parser=etree.HTMLParser())
parser = AdvertListParser()
for advert in parser.parse(root_node):
    print str(advert)
