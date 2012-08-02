# encoding=utf8
'''
Процессоры данных - сохранение и загрузка в/из БД.
@author: Mic, 2012
'''

from pymongo import Connection

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
            cls._connection = Connection('192.168.1.3', 27017)
        return cls._connection
    
    @classmethod
    def get(cls):
        '''
        Возвращает объект БД.
        @return: Database
        '''
        connection = cls._get_connection()
        return connection['tomsk-estate']

class AdvertProcessor(object):
    
    # Поля, которые нужно сохранять в БД:
    FIELDS = ('external_id', 'age', 'district', 'address', 'floor_number', 'floor_count', 
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
    
    def _get_collection(self):
        '''
        Возвращает коллекцию для объявлений.
        @return: Collection
        '''
        return MongoDb.get().adverts
    
    def get_by_external_id(self, external_id):
        '''
        Находит объявление по внешнему идентификатору.
        @param external_id: int
        @return: Advert
        '''
        collection = self._get_collection()
        document = collection.find_one({'external_id': external_id})
        return self._convert_document_to_advert(document)
    
    def save(self, advert):
        '''
        Сохраняет объявление в БД.
        @param advert: Advert
        '''
        collection = self._get_collection()
        document = self._convert_advert_to_document(advert)
        advert.id = collection.insert(document)
