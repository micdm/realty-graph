# coding=utf-8
'''
Парсеры данных.
@author: Mic, 2012
'''

from datetime import date
from re import search, UNICODE

from lxml import etree

from dmte.models import Advert

class AdvertParser(object):
    '''
    Парсер объявлений.
    '''
    
    def _get_external_id(self, advert_node):
        '''
        Возвращает внешний идентификатор объявления.
        @param advert_node: Element
        @return: int
        '''
        xpath = etree.XPath('.//a[@class="visited_ads"]')
        node = xpath(advert_node)[0]
        found = search('id=(\d+)', node.attrib['href'])
        if found is None:
            raise Exception('no external id found')
        return found.group(1)
    
    def _get_age(self, advert_node):
        '''
        Возвращает возраст (первичное, вторичное).
        @param advert_node: Element
        @return: str
        '''
        xpath = etree.XPath('.//p[2]')
        node = xpath(advert_node)[0]
        found = search(u'\((\w+)\)', node.text, UNICODE)
        if found is None:
            raise Exception('no age found')
        return found.group(1)
    
    def _get_normalized_district(self, district):
        '''
        Возвращает нормализованное название района.
        @param district: str
        @return: str
        '''
        if district == 'Кировском':
            return 'Кировский'
        if district == 'Ленинском':
            return 'Ленинский'
        if district == 'Октябрьском':
            return 'Октябрьский'
        if district == 'Советском':
            return 'Советский'
        if district == 'Томском':
            return 'Томский'
        raise Exception('can not normalize district "%s"'%district)
    
    def _get_district(self, advert_node):
        '''
        Возвращает район.
        @param advert_node: Element
        @return: str
        '''
        xpath = etree.XPath('.//p[2]')
        node = xpath(advert_node)[0]
        found = search(u'в (\w+) районе', node.text, UNICODE)
        if found is None:
            raise Exception('no district found')
        return self._get_normalized_district(found.group(1))
    
    def _get_address(self, advert_node):
        '''
        Возвращает адрес.
        @param advert_node: Element
        @return: str
        '''
        xpath = etree.XPath('.//p[2]/a[@class="map_link"]')
        node = xpath(advert_node)[0]
        return node.text
    
    def _get_floor_number(self, advert_node):
        '''
        Возвращает номер этажа.
        @param advert_node: Element
        @return: int
        '''
        xpath = etree.XPath('.//p[2]')
        node = xpath(advert_node)[0]
        found = search(u'на (\d+)-м этаже', node.text, UNICODE)
        if found is None:
            raise Exception('no floor found')
        return int(found.group(1))
    
    def _get_floor_count(self, advert_node):
        '''
        Возвращает количество этажей.
        @param advert_node: Element
        @return: int
        '''
        xpath = etree.XPath('.//p[2]')
        node = xpath(advert_node)[0]
        found = search(u'в (\d+)-этажном', node.text, UNICODE)
        if found is None:
            raise Exception('no floor found')
        return int(found.group(1))

    def _get_area(self, advert_node):
        '''
        Возвращает площадь.
        @param advert_node: Element
        @return: float
        '''
        xpath = etree.XPath('.//p[2]')
        node = xpath(advert_node)[0]
        node_text = etree.tostring(node, encoding='utf8', method='text').decode('utf8')
        found = search(u'общей площадью (\d+(\.\d+)*)', node_text, UNICODE)
        if found is None:
            raise Exception('no area found')
        return float(found.group(1))
    
    def _get_room_count(self, advert_node):
        '''
        Возвращает количество комнат.
        @param advert_node: Element
        @return: int
        '''
        xpath = etree.XPath('.//a[@class="visited_ads"]')
        node = xpath(advert_node)[0]
        if node.text == u'комнату':
            return None
        found = search(u'(\d+)-комнатную', node.text, UNICODE)
        if found is None:
            raise Exception('no room count found')
        return int(found.group(1))
    
    def _get_price(self, advert_node):
        '''
        Возвращает цену.
        @param advert_node: Element
        @return: float
        '''
        xpath = etree.XPath('.//p[4]/b')
        node = xpath(advert_node)[0]
        return float(node.text) * 1000
    
    def _get_month_number(self, month):
        '''
        Возвращает номер месяца.
        @param month: str
        @return: int
        '''
        if month == u'января':
            return 1
        if month == u'февраля':
            return 2
        if month == u'марта':
            return 3
        if month == u'апреля':
            return 4
        if month == u'мая':
            return 5
        if month == u'июня':
            return 6
        if month == u'июля':
            return 7
        if month == u'августа':
            return 8
        if month == u'сентября':
            return 9
        if month == u'октября':
            return 10
        if month == u'ноября':
            return 11
        if month == u'декабря':
            return 12
        raise Exception('can not define number for month "%s"'%month)
    
    def _get_publication_date(self, advert_node):
        '''
        Возвращает дату публикации объявления.
        @param advert_node: Element
        @return: datetime
        '''
        xpath = etree.XPath('.//p[6]')
        node = xpath(advert_node)[0]
        found = search(u'(\d{1,2}) (\w+) (\d{4})', node.text, UNICODE)
        if found is None:
            raise Exception('no publication date found')
        day, month, year = int(found.group(1)), self._get_month_number(found.group(2)), int(found.group(3))
        return date(year, month, day)
    
    def parse(self, advert_node):
        '''
        Возвращает заполненное объявление.
        @param advert_node: Element
        @return: Advert
        '''
        advert = Advert()
        advert.external_id = self._get_external_id(advert_node)
        advert.age = self._get_age(advert_node)
        advert.district = self._get_district(advert_node)
        advert.address = self._get_address(advert_node)
        advert.floor_number = self._get_floor_number(advert_node)
        advert.floor_count = self._get_floor_count(advert_node)
        advert.area = self._get_area(advert_node)
        advert.room_count = self._get_room_count(advert_node)
        advert.price = self._get_price(advert_node)
        advert.publication_date = self._get_publication_date(advert_node)
        return advert
    
class AdvertListParser(object):
    '''
    Парсер списка объявлений.
    '''
    
    def parse(self, root_node):
        '''
        Разбирает и возвращает список объявлений.
        @param root_node: Element
        @return: list
        '''
        for advert_node in root_node.findall('.//tr[@class="realty_ad_text_1"]'):
            parser = AdvertParser()
            yield parser.parse(advert_node)
