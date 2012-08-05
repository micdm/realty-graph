# encoding=utf8
'''
Построение графиков.
@author: Mic, 2012
'''

from datetime import datetime, timedelta

import Image, ImageDraw

from dmte.processors import AdvertProcessor

class GraphBuilder(object):
    '''
    Построитель графиков.
    '''
    
    # Интервал для выборки данных (дни):
    ADVERT_MAX_AGE = 180
    
    def _get_adverts(self, **kwargs):
        '''
        Возвращает объявления по критериям.
        @return: list
        '''
        processor = AdvertProcessor()
        kwargs['publication_date'] = {'$gt': datetime.utcnow() - timedelta(days=self.ADVERT_MAX_AGE)}
        return processor.get_by_info(**kwargs)
    
    def _group_by_date(self, adverts):
        '''
        Возвращает общие площадь и сумму объявлений, сгруппированные по дате.
        @param adverts: list
        @return: dict
        '''
        groupped = {}
        for advert in adverts:
            if advert.publication_date not in groupped:
                groupped[advert.publication_date] = {
                    'area': 0,
                    'price': 0,
                }
            group = groupped[advert.publication_date]
            group['area'] += advert.area
            group['price'] += advert.price
        return groupped
    
    def _get_average(self, groupped):
        '''
        Возвращает средние цены за квадратный метр, сгруппированные по дате.
        @param groupped: dict
        @return: dict
        '''
        return dict((key, group['price'] / group['area']) for key, group in groupped.items())
    
    def _build_graph(self, average):
        image_width = 600
        image_height = 600
        image = Image.new('RGB', (image_width, image_height), 0xFFFFFF)
        draw = ImageDraw.Draw(image)
        if average:
            prepared = [(int(key.strftime('%s')), value) for key, value in average.items()]
            prepared.sort(key=lambda item: item[0])
            x_values = [value for value, _ in prepared]
            y_values = [value for _, value in prepared]
            step_x = image_width / float(max(x_values) - min(x_values))
            step_y = image_height / float(max(y_values))
            points = [((point_x - min(x_values)) * step_x, image_height - point_y * step_y) for point_x, point_y in zip(x_values, y_values)]
            draw.line(points, fill=0, width=1)
        image.save('/tmp/image.png', format='PNG')
        return open('/tmp/image.png').read()
    
    def build(self, **kwargs):
        '''
        Строит график.
        '''
        adverts = self._get_adverts(**kwargs)
        groupped = self._group_by_date(adverts)
        average = self._get_average(groupped)
        return self._build_graph(average)
