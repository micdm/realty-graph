# coding=utf8
'''
Модели данных.
@author: Mic, 2012
'''

class Advert(object):
    '''
    Объявление.
    '''
    
    def __init__(self):
        self.id = None
        self.external_id = None
        self.age = None
        self.district = None
        self.address = None
        self.floor_number = None
        self.floor_count = None
        self.area = None
        self.room_count = None
        self.price = None
        self.publication_date = None
        
    def __str__(self):
        attrs = []
        for key, value in self.__dict__.items():
            attrs.append('%s=%s'%(key, value))
        return 'Advert(%s)'%', '.join(attrs)
