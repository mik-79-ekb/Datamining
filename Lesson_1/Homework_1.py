"""
Источник: https://5ka.ru/special_offers/
Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы
результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json файлы,
для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно соответсвующие данной категории.
пример структуры данных для файла:
нейминг ключей можно делать отличным от примера

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""
import json
import time
from pathlib import Path
import requests

cat_product_path = get_save_path('Parser_results')
url = 'https://5ka.ru/api/v2/categories/'
response = requests.get(url)
cat = response.json()
for x in range(len(cat)):
    url_cat = f'https://5ka.ru/api/v2/special_offers/?categories={cat[x]["parent_group_code"]}&ordering=&page=1&price_promo__gte=&price_promo__lte=&100&search=&store'
    headers = {
                "User-Agent": "Santa Claus Ho-ho-ho"
            }
    response = requests.get(url_cat, headers=headers)
    prod = response.json()
    data = {"name": cat[x]['parent_group_name'],
                "code": cat[x]['parent_group_code'],
                "products": prod['results']}
    with open(f"Parser_results/{cat[x]['parent_group_code']}.json", 'w', encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False)
