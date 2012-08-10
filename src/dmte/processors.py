# encoding=utf8
'''
Процессоры данных - сохранение и загрузка в/из БД.
@author: Mic, 2012
'''

from pymongo import Connection

from dmte.conf import settings
from dmte.models import Advert

class MongoDb(object):
    '''
    Для работы с БД.
    '''
    
    # Текущее подключение к БД:
    _connection = None
    
    @classmethod
    def _get_connection(cls):
        '''
        Возвращает подключение к БД.
        Если подключения еще нет, устанавливает его.
        @return: Connection
        '''
        if cls._connection is None:
            cls._connection = Connection(settings.MONGO_DB['host'], settings.MONGO_DB['port'])
        return cls._connection
    
    @classmethod
    def get(cls):
        '''
        Возвращает объект БД.
        @return: Database
        '''
        connection = cls._get_connection()
        db_name = settings.MONGO_DB['db_name']
        return connection[db_name]

class AdvertProcessor(object):
    
    # Поля, которые нужно сохранять в БД:
    FIELDS = ('external_id', 'type', 'district', 'address', 'floor_number', 'floor_count', 
              'area', 'room_count', 'price', 'publication_date')

    def _convert_advert_to_document(self, advert):
        '''
        Преобразовывает объявление в документ.
        @param advert: Advert
        @return: dict
        '''
        document = {}
        if advert.id is not None:
            document['_id'] = advert.id
        for field_name in self.FIELDS:
            document[field_name] = getattr(advert, field_name)
        return document
    
    def _convert_document_to_advert(self, document):
        '''
        Преобразовывает документ в объявление.
        @param document: dict
        @return: Advert
        '''
        if document is None:
            return None
        advert = Advert()
        advert.id = document['_id']
        for field_name in self.FIELDS:
            setattr(advert, field_name, document[field_name])
        return advert
    
    @property
    def _collection(self):
        '''
        Возвращает коллекцию для объявлений.
        @return: Collection
        '''
        return MongoDb.get().adverts
    
    def get_aggregated(self):
        '''
        Возвращает все возможные значения для полей.
        @return: dict
        '''
        aggregated = {}
        for field in ('type', 'district', 'floor_number', 'room_count'):
            values = self._collection.distinct(field)
            aggregated[field] = sorted(values)
        aggregated['floor_number'] = filter(lambda value: value <= 10, aggregated['floor_number'])
        aggregated['room_count'] = filter(lambda value: value <= 5, aggregated['room_count'])
        return aggregated
    
    def get_by_external_id(self, external_id):
        '''
        Находит объявление по внешнему идентификатору.
        @param external_id: int
        @return: Advert
        '''
        document = self._collection.find_one({'external_id': external_id})
        return self._convert_document_to_advert(document)
    
    def get_by_info(self, params):
        '''
        Возвращает список объявлений по указанным параметрам.
        @param params: dict
        @return: list
        '''
        documents = self._collection.find(params)
        return map(self._convert_document_to_advert, documents)
    
    def save(self, advert):
        '''
        Сохраняет объявление в БД.
        @param advert: Advert
        '''
        document = self._convert_advert_to_document(advert)
        advert.id = self._collection.insert(document)
