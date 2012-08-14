# encoding=utf8
'''
Построение графиков.
@author: Mic, 2012
'''

from datetime import datetime, timedelta
from StringIO import StringIO

import Image, ImageDraw, ImageFont

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
    IMAGE_HEIGHT = 330
    
    # Размеры графика:
    GRAPH_WIDTH = 900
    GRAPH_HEIGHT = 300
    
    # Цвета и шрифты:
    BACKGROUND_COLOR = 'white'
    BORDER_COLOR = 'lightgray'
    LINE_COLOR = 'black'
    CURRENT_LEVEL_COLOR = 'lightgray'
    TEXT_LABEL_COLOR = 'lightgray'
    TEXT_COLOR = 'black'
    TEXT_FONT = ImageFont.truetype('/usr/share/fonts/truetype/ttf-dejavu/DejaVuSerif.ttf', 12)
    
    def _get_new_image(self):
        '''
        Возвращает новую картинку.
        @return: Image
        '''
        return Image.new('RGB', (self.IMAGE_WIDTH, self.IMAGE_HEIGHT), self.BACKGROUND_COLOR)
    
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
    
    def _get_bounds(self, points):
        '''
        Возвращает граничные точки из списка.
        @param points: list
        @return: dict
        '''
        if not points:
            return None
        return {
            'min_x': min(points, key=lambda point: point.x),
            'max_x': max(points, key=lambda point: point.x),
            'min_y': min(points, key=lambda point: point.y),
            'max_y': max(points, key=lambda point: point.y),
        }
    
    def _get_value_x(self, min_value, max_value, value):
        '''
        Возвращает X-позицию для значения.
        @param min_value: float
        @param max_value: float
        @param value: float
        @return: float
        '''
        return self.GRAPH_WIDTH * (value - min_value) / float(max_value - min_value)
    
    def _get_value_y(self, min_value, max_value, value):
        '''
        Возвращает Y-позицию для значения.
        @param min_value: float
        @param max_value: float
        @param value: float
        @return: float
        '''
        return self.GRAPH_HEIGHT - self.GRAPH_HEIGHT * (value - min_value) / float(max_value - min_value)
    
    def _get_point_coords(self, point, bounds):
        '''
        Возвращает координаты точки на графике.
        @param point: GraphPoint
        @param bounds: dict
        @return: float, float
        '''
        x = self._get_value_x(bounds['min_x'].x, bounds['max_x'].x, point.x)
        y = self._get_value_y(0, bounds['max_y'].y, point.y)
        return x, y
    
    def _draw_border(self, draw):
        '''
        Рисует рамку.
        @param draw: Draw
        '''
        draw.rectangle((0, 0, self.GRAPH_WIDTH - 1, self.GRAPH_HEIGHT - 1), outline=self.BORDER_COLOR)
    
    def _draw_points(self, draw, points, bounds):
        '''
        Рисует точки и соединяет их линией.
        @param draw: Draw
        @param points: list
        @param bounds: dict
        '''
        if not points:
            return
        points.sort(key=lambda point: point.x)
        prev_x, prev_y = None, None
        for point in points:
            x, y = self._get_point_coords(point, bounds)
            if prev_x is not None and prev_y is not None:
                coords = (prev_x, prev_y, x, y)
                draw.line(coords, fill=self.LINE_COLOR)
            prev_x, prev_y = x, y

    def _draw_label(self, draw, x, y, text):
        '''
        Рисует текстовую метку.
        @param x: float
        @param y: float
        @param text: str
        '''
        width, height = draw.textsize(text)
        if x + width > self.GRAPH_WIDTH:
            x -= width
        if y + height > self.GRAPH_HEIGHT:
            y -= height
        draw.rectangle((x - 2, y - 2, x + width + 2, y + height + 2), fill=self.TEXT_LABEL_COLOR)
        draw.text((x, y), text, fill=self.TEXT_COLOR)

    def _draw_labels(self, draw, bounds):
        '''
        Рисует необходимые текстовые метки.
        @param draw: Draw
        @param bounds: dict
        '''
        if bounds is None:
            return
        for point in bounds.values():
            x, y = self._get_point_coords(point, bounds)
            self._draw_label(draw, x, y, '%s (%s)'%(int(point.y), point.label_x))
            
    def _draw_current_level(self, draw, bounds):
        '''
        Рисует горизонтальную линию - уровень цены на данный момент.
        @param draw: Draw
        @param bounds: dict
        '''
        if bounds is None:
            return
        x, y = self._get_point_coords(bounds['max_x'], bounds)
        draw.line((0, y, x, y), fill=self.CURRENT_LEVEL_COLOR)
        
    def _draw_legend(self, draw, text):
        '''
        Рисует подпись к графику.
        @param text: str
        '''
        draw.text((0, self.GRAPH_HEIGHT + 2), text, fill=self.TEXT_COLOR, font=self.TEXT_FONT)

    def draw(self, points, legend):
        '''
        Рисует по точкам график и возвращает тело картинки.
        @param points: list
        @param legend: str
        @return: str
        '''
        image = self._get_new_image()
        draw = ImageDraw.Draw(image)
        bounds = self._get_bounds(points)
        self._draw_border(draw)
        self._draw_points(draw, points, bounds)
        self._draw_labels(draw, bounds)
        self._draw_current_level(draw, bounds)
        self._draw_legend(draw, legend)
        return self._get_image_body(image)

class GraphBuilder(object):
    '''
    Построитель графиков.
    '''
    
    # Интервал для выборки данных (дни):
    ADVERT_MAX_AGE = 180
    
    # Максимальное значение отношения суммы объявления к средней сумме группы,
    # после достижения которого объявление считается плохим:
    FIX_RATIO = 3.0
    
    def _get_adverts(self, params):
        '''
        Возвращает объявления по критериям.
        @return: list
        '''
        processor = AdvertProcessor()
        params['publication_date'] = {'$gt': datetime.utcnow() - timedelta(days=self.ADVERT_MAX_AGE)}
        return processor.get_by_info(params)
    
    def _get_average(self, adverts):
        '''
        Возвращает среднее для списка объявлений.
        @param adverts: list
        @return: float
        '''
        price = sum(advert.price for advert in adverts)
        area = sum(advert.area for advert in adverts)
        return price / area
    
    def _fix_groupped(self, groupped):
        '''
        Возвращает подправленные данные: убирает объявления, сильно отклоняющиеся
        от средних значений.
        @param groupped: dict
        @return: dict
        '''
        fixed = {}
        for publication_date, adverts in groupped.items():
            total_average = self._get_average(adverts)
            fixed_group = []
            for advert in adverts:
                average = advert.price / advert.area
                if 1 / self.FIX_RATIO < average / total_average < self.FIX_RATIO:
                    fixed_group.append(advert)
            if fixed_group:
                fixed[publication_date] = fixed_group
        return fixed
    
    def _group_by_date(self, adverts):
        '''
        Возвращает объявления, сгруппированные по дате.
        @param adverts: list
        @return: dict
        '''
        groupped = {}
        for advert in adverts:
            if advert.publication_date not in groupped:
                groupped[advert.publication_date] = []
            groupped[advert.publication_date].append(advert)
        return self._fix_groupped(groupped)

    def _get_groupped_average(self, groupped):
        '''
        Возвращает средние цены за квадратный метр, сгруппированные по дате.
        @param groupped: dict
        @return: dict
        '''
        average = {}
        for publication_date, adverts in groupped.items():
            average[publication_date] = self._get_average(adverts)
        return average

    def _get_graph_legend(self, params):
        '''
        Возвращает легенду для графика.
        @param params: dict
        @return: str
        '''
        legend = []
        if 'type' in params:
            legend.append(params['type'].capitalize())
        else:
            legend.append(u'Любого типа')
        if 'district' in params:
            legend.append(u'%s район'%params['district'].capitalize())
        else:
            legend.append(u'любой район')
        if 'floor_number' in params:
            legend.append(u'%s этаж'%params['floor_number'])
        else:
            legend.append(u'любой этаж')
        if 'room_count' in params:
            legend.append(u'%s-комнатное'%params['room_count'])
        else:
            legend.append(u'любое количество комнат')
        return ', '.join(legend) + '.'
    
    def _build_graph(self, average, params):
        '''
        Строит график и возвращает картинку строкой.
        @param average: dict
        @param params: dict
        @return: str
        '''
        points = []
        for publication_date, value in average.items():
            timestamp = int(publication_date.strftime('%s'))
            label = publication_date.strftime('%Y-%m-%d')
            points.append(GraphPoint(timestamp, value, label))
        graph_drawer = GraphDrawer()
        legend = self._get_graph_legend(params)
        return graph_drawer.draw(points, legend)
    
    def build(self, params):
        '''
        Строит график.
        @param params: dict
        @return: str
        '''
        adverts = self._get_adverts(params)
        groupped = self._group_by_date(adverts)
        average = self._get_groupped_average(groupped)
        return self._build_graph(average, params)
