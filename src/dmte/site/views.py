# encoding=utf8
'''
Страницы для сайта.
@author: Mic, 2012
'''

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    '''
    Главная страница.
    '''
    return render_template('index.html', foo='bar')
