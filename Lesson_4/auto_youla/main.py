"""
Источник https://auto.youla.ru/
Обойти все марки авто и зайти на странички объявлений
Собрать след стуркутру и сохранить в БД Монго
Название объявления
Список фото объявления (ссылки)
Список характеристик
Описание объявления
ссылка на автора объявления
дополнительно попробуйте вытащить телефона
"""

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from auto_youla.spiders.autoyoula import AutoyoulaSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule("auto_youla.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(AutoyoulaSpider)
    crawler_process.start()