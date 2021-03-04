# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import os

import pandas as pd

from wsm.config import CSV_PATH


class WebdatascraperPipeline(object):
    def process_item(self, item, spider):
        return item


class DataPipeline(object):
    """ A class that needs a list of ChartItem """

    def __init__(self, data_list):
        self.dataList = data_list
        # self.webDataFrame = pd.DataFrame(data_list, columns=['country', 'icao', 'link', 'file', 'desc', 'club', 'category'])  # aerodrome
        # self.webDataFrame = pd.DataFrame(data_list, columns=['spider', 'category', 'subcategory', 'subsubcategory'])  # amazon
        self.webDataFrame = pd.DataFrame(data_list, columns=['name', 'age', 'birthday', 'nationality', 'hometown', 'ethnicity', 'streams', 'formerteams'])  # twitch

    def process_charts(self):
        pass

    def print_data_list(self):
        """ Prints the chart list """
        print(self.webDataFrame)

    def save_data_list(self, file_name):
        """ Write and saves the chart list to CSV file """
        x = file_name + '__LinkList.csv'
        f = CSV_PATH + x
        print('\nSaving data into a CSV file [{0}]...'.format(x))
        self.webDataFrame.to_csv(f, index=False)

        print('Finished writing the webiste data list file: {0}\n'.format(os.path.abspath(f)))
