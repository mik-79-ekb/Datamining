"""
Продолжить работу с парсером блога GB
Реализовать SQL базу данных посредствам SQLAlchemy
Реализовать реалиционные связи между Постом и Автором, Постом и Тегом, Постом и комментарием, Комментарием и комментарием
"""

import typing
import time
import requests
from urllib.parse import urljoin
import bs4
from database.database import Database


class Gb_Parse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) "
                      "Gecko/20100101 Firefox/88.0"
    }
    __parse_time = 0

    def __init__(self, start_url, db: Database, delay=1.0):
        self.start_url = start_url
        self.db = db
        self.delay = delay
        self.done_urls = set()
        self.tasks = []
        self.tasks_creator({self.start_url, }, self.parse_feed)

    def _get_response(self, url):
        while True:
            next_time = self.__parse_time + self.delay
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            print(f'Response: {response.url}')
            self.__parse_time = time.time()
            if response.status_code in (206, 200):
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
            'post_data': {
                'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                'url': response.url,
                'id': int(soup.find('comments').attrs.get('commentable-id')),
            },
            'author_data': {
                'url': urljoin(response.url, author_name_tag.parent.attrs.get('href')),
                'name': author_name_tag.text,
            },
            'tags_data': [
                {'name': tag.text, 'url': urljoin(response.url, tag.attrs.get('href'))}
                for tag in soup.find_all('a', attrs={'class': 'small'})
            ],
            'comments_data': self.__get_comments(soup.find('comments').attrs.get('commentable-id'))
        }
        self._save(data)

    def _save(self, data: dict):
        self.db.add_post(data)

    def __get_comments(self, post_id):
        api_path = f'api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc'
        response = self._get_response(urljoin(self.start_url, api_path))
        comments_list: dict = response.json()
        data = []
        for item in comments_list:
            data.append(self.__parse_comment(item))
            for cm in item['comment']['children']:
                data.append(self.__parse_comment(cm))
        return data

    def __parse_comment(self, itm):
        return {
            'comment_data': {
                'id': itm['comment']['id'],
                'text': itm['comment']['body'],
                'parent_id': itm['comment']['parent_id'],
                'root_comment_id': itm['comment']['root_comment_id']
            },
            'author_data': {
                'url': itm['comment']['user']['url'],
                'name': itm['comment']['user']['full_name'],
            }
        }


if __name__ == '__main__':
    orm_database = Database('sqlite:///gb_parse.db')
    parser = Gb_Parse('https://gb.ru/posts', orm_database)
    parser.run()