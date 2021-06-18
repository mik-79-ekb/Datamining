ADS = {
    "selector": "//div[@data-marker='catalog-serp']//a[@data-marker='item-title']/@href",
    "callback": "ads_parse"
}

ADS_DATA = {
    "title": {"xpath": "//h1[@class='title-info-title']/span/text()"},
    "price": {"xpath": "//span[@itemprop='price']/@content"},
    "address": {"xpath": "//span[@class='item-address__string']/text()"},
    "parameters": {"xpath": "//ul[@class='item-params-list']/li"},
    "seller": {"xpath": "//div[@data-marker='seller-info/name']/a/@href"},
    "phone": {"xpath": "//img[@data-marker='phone-popup/phone-image']/a/@src"}
}