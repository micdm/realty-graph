# encoding=utf8
'''
Построение графиков.
@author: Mic, 2012
'''

from datetime import datetime, timedelta
from StringIO import StringIO

import Image, ImageDraw

from dmte.processors import AdvertProcessor

class GraphPoint(object):
    '''
    Точка на графике.
    '''
    
    def __init__(self, x, y, label_x=None, label_y=None):
        '''
        @param x: float
        @param y: float
        @param label_x: str
        @param label_y: str
        '''
        self.x = x
        self.y = y
        self.label_x = label_x
        self.label_y = label_y
        
class GraphDrawer(object):
    '''
    Рисовальщик графика.
    '''
    
    # Размеры картинки:
    IMAGE_WIDTH = 900
    IMAGE_HEIGHT = 300
    
    # Цвета:
    BACKGROUND_COLOR = 'white'
    LINE_COLOR = 'black'
    TEXT_LABEL_COLOR = 'lightgray'
    TEXT_COLOR = 'black'
    
    def _get_new_image(self):
        '''
        Возвращает новую картинку.
        @return: Image
        '''
        return Image.new('RGB', (self.IMAGE_WIDTH + 1, self.IMAGE_HEIGHT + 1), self.BACKGROUND_COLOR)
    
    def _get_image_body(self, image):
        '''
        Возвращает тело картинки.
        @param image: Image
        @return: str
        '''
        output = StringIO()
        image.save(output, format='PNG')
        output.seek(0)
        return output.read()
    
    def _get_value_x(self, min_value, max_value, value):
        '''
        Возвращает X-позицию для значения.
        @param min_value: float
        @param max_value: float
        @param value: float
        @return: float
        '''
        return self.IMAGE_WIDTH * (value - min_value) / (max_value - min_value)
    
    def _get_value_y(self, min_value, max_value, value):
        '''
        Возвращает Y-позицию для значения.
        @param min_value: float
        @param max_value: float
        @param value: float
        @return: float
        '''
        return self.IMAGE_HEIGHT - self.IMAGE_HEIGHT * (value - min_value) / (max_value - min_value)
    
    def _draw_label(self, draw, x, y, text):
        '''
        Рисует текстовую метку.
        @param x: float
        @param y: float
        @param text: str
        '''
        width, height = draw.textsize(text)
        if x + width > self.IMAGE_WIDTH:
            x -= width
        if y + height > self.IMAGE_HEIGHT:
            y -= height
        draw.rectangle((x - 2, y - 2, x + width + 2, y + height + 2), fill=self.TEXT_LABEL_COLOR)
        draw.text((x, y), text, fill=self.TEXT_COLOR)
    
    def _draw_points(self, draw, points):
        '''
        Рисует точки и соединяет их линией.
        @param draw: Draw
        @param points: list
        '''
        if not points:
            return
        points.sort(key=lambda point: point.x)
        min_x_point, max_x_point = min(points, key=lambda point: point.x), max(points, key=lambda point: point.x)
        min_y_point, max_y_point = min(points, key=lambda point: point.y), max(points, key=lambda point: point.y)
        prev_x, prev_y = None, None
        for point in points:
            x = self._get_value_x(min_x_point.x, max_x_point.x, point.x)
            y = self._get_value_y(min_y_point.y, max_y_point.y, point.y)
            if prev_x is not None and prev_y is not None:
                coords = (prev_x, prev_y, x, y)
                draw.line(coords, fill=self.LINE_COLOR)
            prev_x, prev_y = x, y
        for point in (min_x_point, max_x_point, min_y_point, max_y_point):
            x = self._get_value_x(min_x_point.x, max_x_point.x, point.x)
            y = self._get_value_y(min_y_point.y, max_y_point.y, point.y)
            self._draw_label(draw, x, y, '%s (%s)'%(int(point.y), point.label_x))

    def draw(self, points):
        '''
        Рисует по точкам график и возвращает тело картинки.
        @param points: list
        @return: str
        '''
        image = self._get_new_image()
        draw = ImageDraw.Draw(image)
        self._draw_points(draw, points)
        return self._get_image_body(image)

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
    
    def _get_filtered(self, average):
        '''
        Возвращает отфильтрованные данные без резких пиков.
        @param average: dict
        @return: dict
        '''
        result = {}
        prev_value = None
        for key, value in average.items():
            if prev_value is None:
                prev_value = value
                continue
            percent = value / prev_value
            if percent > 0.6 and percent < 1.4:
                result[key] = value
                prev_value = value
        return result
    
    def _build_graph(self, average):
        '''
        Строит график и возвращает картинку строкой.
        @param average: dict
        @return: str
        '''
        points = []
        for publication_date, value in average.items():
            timestamp = int(publication_date.strftime('%s'))
            label = publication_date.strftime('%Y-%m-%d')
            points.append(GraphPoint(timestamp, value, label))
        graph_drawer = GraphDrawer()
        return graph_drawer.draw(points)
    
    def build(self, **kwargs):
        '''
        Строит график.
        @return: str
        '''
        adverts = self._get_adverts(**kwargs)
        groupped = self._group_by_date(adverts)
        average = self._get_average(groupped)
        filtered = self._get_filtered(average)
        return self._build_graph(filtered)
