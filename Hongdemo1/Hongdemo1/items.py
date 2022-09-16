# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Hongdemo1Item(scrapy.Item):
    # define the fields for your item here like:
    next_page_src = scrapy.Field()
    next_page_title = scrapy.Field()
    pass
