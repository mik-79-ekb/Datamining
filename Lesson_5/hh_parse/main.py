"""
Источник https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113
вакансии удаленной работы.

Задача: Обойти с точки входа все вакансии и собрать след данные:

1. название вакансии
2. оклад (строкой от до или просто сумма)
3. Описание вакансии
4. ключевые навыки - в виде списка названий
5. ссылка на автора вакансии

Перейти на страницу автора вакансии,
собрать данные:

1. Название
2. сайт ссылка (если есть)
3. сферы деятельности (списком)
4. Описание

Обойти и собрать все вакансии данного автора.
"""

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hh_parse.spiders.hh_remote import HhRemoteSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule("hh_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HhRemoteSpider)
    crawler_process.start()