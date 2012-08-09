# encoding=utf8
'''
Страницы для сайта.
@author: Mic, 2012
'''

from flask import Flask, make_response, request, render_template, url_for

from dmte.graphics import GraphBuilder
from dmte.processors import AdvertProcessor

app = Flask(__name__)

@app.route('/')
def index():
    '''
    Главная страница.
    '''
    processor = AdvertProcessor()
    aggregated = processor.get_aggregated()
    graph_url = url_for('graph', type=request.args.get('type') or 'all', district=request.args.get('district') or 'all',
                        floor_number=request.args.get('floor_number') or 0, room_count=request.args.get('room_count') or 0)
    return render_template('index.html', aggregated=aggregated, graph_url=graph_url)

def _validate_graph_param(aggregated, params, key, default):
    '''
    Проверяет отдельный параметр графика.
    @param aggregated: dict
    @param params: dict
    @param key: str
    @param default: mixed
    '''
    if params[key] in aggregated[key]  :
        return True
    if params[key] == default:
        del params[key]
        return True
    return False

def _validate_graph_params(params):
    '''
    Проверяет параметры графика.
    '''
    processor = AdvertProcessor()
    aggregated = processor.get_aggregated()
    if not _validate_graph_param(aggregated, params, 'type', 'all'):
        return False
    if not _validate_graph_param(aggregated, params, 'district', 'all'):
        return False
    if not _validate_graph_param(aggregated, params, 'floor_number', 0):
        return False
    if not _validate_graph_param(aggregated, params, 'room_count', 0):
        return False
    return True

@app.route('/graph/<type>/<district>/<int:floor_number>/<int:room_count>/')
def graph(**kwargs):
    '''
    Генератор графиков.
    '''
    if not _validate_graph_params(kwargs):
        return None, 404
    graph_builder = GraphBuilder()
    graph = graph_builder.build(kwargs)
    response = make_response(graph)
    response.mimetype = 'image/png'
    return response
