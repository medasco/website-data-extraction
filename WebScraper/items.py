# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DataItem(scrapy.Item):
    """ Class representing an Airport Chart item """
    # aerodrome
    country = scrapy.Field()
    category = scrapy.Field()
    icao = scrapy.Field()
    desc = scrapy.Field()
    link = scrapy.Field()
    file = scrapy.Field()
    club = scrapy.Field()

    # amazon
    spider = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    subsubcategory = scrapy.Field()

    # twitch
    Page = scrapy.Field()
    Alias = scrapy.Field()
    Name = scrapy.Field()
    Age = scrapy.Field()
    Birthday = scrapy.Field()
    Nationality = scrapy.Field()
    Hometown = scrapy.Field()
    Ethnicity = scrapy.Field()
    Streams = scrapy.Field()
    FormerTeams = scrapy.Field()
    Team = scrapy.Field()
    TwitchStatus = scrapy.Field()
    TwitchFollowers = scrapy.Field()
    TwitchChannelViews = scrapy.Field()
    Family = scrapy.Field()
    NameOrigins = scrapy.Field()
    GamingOrigins = scrapy.Field()
    ProfessionalGaming = scrapy.Field()
    StreamingHours = scrapy.Field()
    Accomplishments = scrapy.Field()
    Quotes = scrapy.Field()
    Relationships = scrapy.Field()
    Income = scrapy.Field()
    OtherInterests = scrapy.Field()
    Accomplishments = scrapy.Field()
    Sources = scrapy.Field()
    InterestingFacts = scrapy.Field()
    AdviceForStreamers = scrapy.Field()
