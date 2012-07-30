# coding=utf-8

from urllib import urlopen

def get_page_content(url):
    '''
    Скачивает и возвращает содержимое страницы.
    @param url: str
    @return: str
    '''
    response = urlopen(url)
    response_body = response.read()
    return response_body.decode('cp1251')
