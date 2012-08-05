# encoding=utf8
'''
Парсеры данных.
@author: Mic, 2012
'''

from datetime import datetime
from re import search, UNICODE

from lxml import etree

from dmte.log import logger
from dmte.models import Advert

class ParserException(Exception):
    '''
    Ошибка при разборе.
    '''

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
            raise ParserException('no external id found')
        return found.group(1)
    
    def _get_type(self, advert_node):
        '''
        Возвращает тип (первичное, вторичное).
        @param advert_node: Element
        @return: str
        '''
        xpath = etree.XPath('.//p[2]')
        node = xpath(advert_node)[0]
        found = search(u'\((\w+)\)', node.text, UNICODE)
        if found is None:
            raise ParserException('no type found')
        return found.group(1)
    
    def _get_normalized_district(self, district):
        '''
        Возвращает нормализованное название района.
        @param district: str
        @return: str
        '''
        if district == u'Кировском':
            return u'кировский'
        if district == u'Ленинском':
            return u'ленинский'
        if district == u'Октябрьском':
            return u'октябрьский'
        if district == u'Советском':
            return u'советский'
        if district == u'Томском':
            return u'томский'
        raise ParserException(u'can not normalize district "%s"'%district.encode('utf8'))
    
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
            raise ParserException('no district found')
        return self._get_normalized_district(found.group(1))
    
    def _get_address(self, advert_node):
        '''
        Возвращает адрес.
        @param advert_node: Element
        @return: str
        '''
        xpath = etree.XPath('.//p[2]/a[@class="map_link"]')
        nodes = xpath(advert_node)
        if not nodes:
            raise ParserException('no address found')
        return nodes[0].text
    
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
            raise ParserException('no floor found')
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
            raise ('no floor found')
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
            raise ParserException('no area found')
        return float(found.group(1))
    
    def _get_room_count(self, advert_node):
        '''
        Возвращает количество комнат.
        @param advert_node: Element
        @return: int
        '''
        xpath = etree.XPath('.//a[@class="visited_ads"]')
        node = xpath(advert_node)[0]
        found = search(u'(\d+)-комнатную', node.text, UNICODE)
        if found is None:
            raise ParserException('no room count found')
        return int(found.group(1))
    
    def _get_price(self, advert_node):
        '''
        Возвращает цену.
        @param advert_node: Element
        @return: float
        '''
        xpath = etree.XPath('.//p[@style="margin: 10px 0 0 2px;"]/b')
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
        raise ParserException('can not define number for month "%s"'%month.encode('utf8'))
    
    def _get_publication_datetime(self, advert_node):
        '''
        Возвращает дату публикации объявления.
        @param advert_node: Element
        @return: datetime
        '''
        xpath = etree.XPath('.//p[@class="absmiddle"]')
        node = xpath(advert_node)[0]
        if u'Опубликовано сегодня' in node.text:
            return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        found = search(u'(\d{1,2}) (\w+) (\d{4})', node.text, UNICODE)
        if found is None:
            raise ParserException('no publication date found')
        day, month, year = int(found.group(1)), self._get_month_number(found.group(2)), int(found.group(3))
        return datetime(year, month, day)
    
    def parse(self, advert_node):
        '''
        Возвращает заполненное объявление.
        @param advert_node: Element
        @return: Advert
        '''
        advert = Advert()
        advert.external_id = self._get_external_id(advert_node)
        advert.type = self._get_type(advert_node)
        advert.district = self._get_district(advert_node)
        advert.address = self._get_address(advert_node)
        advert.floor_number = self._get_floor_number(advert_node)
        advert.floor_count = self._get_floor_count(advert_node)
        advert.area = self._get_area(advert_node)
        advert.room_count = self._get_room_count(advert_node)
        advert.price = self._get_price(advert_node)
        advert.publication_date = self._get_publication_datetime(advert_node)
        return advert
    
class AdvertListParser(object):
    '''
    Парсер списка объявлений.
    '''
    
    def parse_adverts(self, root_node):
        '''
        Разбирает и возвращает список объявлений.
        @param root_node: Element
        @return: list
        '''
        for advert_node in root_node.findall('.//table[@class="realty"]//tr[@class]'):
            parser = AdvertParser()
            try:
                yield parser.parse(advert_node)
            except ParserException as e:
                logger.warning('can not parse advert: %s', e)
            
    def parse_next_page_address(self, root_node):
        '''
        Находит и возвращает адрес следующей страницы.
        @param root_node: Element
        @return: str
        '''
        xpath = etree.XPath('.//span[@class="pager_next"]/a')
        nodes = xpath(root_node)
        if not nodes:
            return None
        return nodes[0].attrib['href']
