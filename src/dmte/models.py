# encoding=utf8
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
        return 'Advert(#%s)'%self.external_id
