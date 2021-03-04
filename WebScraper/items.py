# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DataItem(scrapy.Item):
    """ Class representing an Airport Chart item """
    # country = scrapy.Field()
    # category = scrapy.Field()
    # icao = scrapy.Field()
    # desc = scrapy.Field()
    # link = scrapy.Field()
    # file = scrapy.Field()
    # club = scrapy.Field()

    # amazon
    spider = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    subsubcategory = scrapy.Field()

    # twitch
    name = scrapy.Field()
    age = scrapy.Field()
    birthday = scrapy.Field()
    nationality = scrapy.Field()
    hometown = scrapy.Field()
    ethnicity = scrapy.Field()
    streams = scrapy.Field()
    formerteams = scrapy.Field()