"""
Источник https://gb.ru/posts/
Необходимо обойти все записи в блоге и извлеч из них информацию следующих полей:
url страницы материала
Заголовок материала
Первое изображение материала (Ссылка)
Дата публикации (в формате datetime)
имя автора материала
ссылка на страницу автора материала
комментарии в виде (автор комментария и текст комментария)
Структуру сохраняем в MongoDB
"""

import typing
import time
import requests
from urllib.parse import urljoin
import bs4
import pymongo


class GB_Parse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) "
                      "Gecko/20100101 Firefox/88.0"
    }
    __parse_time = 0
    __comments_url = 'api/v2/comments?commentable_type=Post&commentable_id='

    def __init__(self, start_url, db, delay=1.0):
        self.start_url = start_url
        self.delay = delay
        self.done_urls = set()
        self.tasks = []
        self.db = db
        self.tasks_creator({self.start_url, }, self.parse_feed)

    def _get_response(self, url):
        while True:
            next_time = self.__parse_time + self.delay
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            print(f'Response: {response.url}')
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            response = self._get_response(url)
            return callback(response)
        return task

    def tasks_creator(self, urls: set, callback: typing.Callable):
        urls_set = urls - self.done_urls
        for url in urls_set:
            self.tasks.append(
                self.get_task(url, callback)
            )
            self.done_urls.add(url)

    def run(self):
        while True:
            try:
                task = self.tasks.pop(0)
                task()
            except IndexError:
                break

    def parse_feed(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        ul_pagination = soup.find('ul', attrs={'class': 'gb__pagination'})
        pagination_links = set(
            urljoin(response.url, itm.attrs.get('href'))
            for itm in ul_pagination.find_all('a') if
            itm.attrs.get('href')
        )
        self.tasks_creator(pagination_links, self.parse_feed)
        post_wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})
        self.tasks_creator(
            set(
                urljoin(response.url, itm.attrs.get('href'))
                for itm in post_wrapper.find_all('a', attrs={'class': 'post-item__title'}) if
                itm.attrs.get('href')
            ),
            self.parse_post
        )

    def parse_post(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        author_name_tag = soup.find('div', attrs={'itemprop': 'author'})
        data = {
            'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
            'time_published': soup.find("time", attrs={'itemprop': 'datePublished'}).get('datetime'),
            'by_author': {
            'url': urljoin(response.url, author_name_tag.parent.attrs['href']),
            'name': author_name_tag.text
            },
            'img': soup.find('div', attrs={'itemprop': 'articleBody'}).find('img').attrs.get('src'),
            'url': response.url,
            'comments': self.__get_comments(soup.find('comments').attrs.get('commentable-id'))
        }
        self._save(data)

    def __get_comments(self, post_id):
        api_path = f'{self.__comments_url}{post_id}&order=desc'
        response = self._get_response(urljoin(self.start_url, api_path))
        comments_list: dict = response.json()
        data = []
        for itm in comments_list:
            data.append({'author': itm['comment']['user']['full_name'], 'text': itm['comment']['body']})
        return data

    def _save(self, data: dict):
        collection = self.db['gb_blog_parse']
        collection.insert_one(data)


if __name__ == '__main__':
    client_db = pymongo.MongoClient('mongodb://localhost:27017')
    db = client_db['HW2_gb_parse']
    parser = GB_Parse('https://gb.ru/posts', db)
    parser.run()