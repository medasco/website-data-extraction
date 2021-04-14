# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import os
import json

import pandas as pd

from wsm.config import SAVING_PATH


class WebdatascraperPipeline(object):
    def process_item(self, item, spider):
        return item


class DataPipeline(object):
    """ A class that needs a list of ChartItem """

    def __init__(self, data_list):
        self.dataList = data_list
        # self.webDataFrame = pd.DataFrame(data_list, columns=['country', 'icao', 'link', 'file', 'desc', 'club', 'category'])  # aerodrome
        # self.webDataFrame = pd.DataFrame(data_list, columns=['spider', 'category', 'subcategory', 'subsubcategory'])  # amazon
        self.webDataFrame = pd.DataFrame(data_list, columns=['Page','Alias', 'Name', 'Age', 'Birthday', 'Nationality',
                                                             'Hometown', 'Ethnicity', 'Streams', 'FormerTeams', 'Team',
                                                             'TwitchStatus', 'TwitchFollowers', 'TwitchChannelViews', 'InfoSection'])  # twitch

    def process_data(self):
        pass

    def print_data_list(self):
        """ Prints the chart list """
        print('\n{0}'.format(self.webDataFrame))

    def save_data_list(self, file_name):
        """ Write and saves the chart list to CSV file """
        x = file_name + '__LinkList.csv'
        f = SAVING_PATH + x
        print('\nSaving data into a CSV file [{0}]...'.format(x))
        self.webDataFrame.to_csv(f, index=False)

        print('Finished writing the webiste data list file: {0}\n'.format(
            os.path.abspath(f)))

    def remove_duplicate_rows(self, file_name, out_file):
        df = pd.read_csv(file_name)
        df.drop_duplicates(inplace=True)
        df.to_csv(out_file, index=False)


class JsonPipeline(object):
    """ A class that needs data to be written as JSON file """

    def __init__(self, data):
        self.data = data

        self.old = None
        self.new = None
        self.tmp = None

    def write_json(self, file_name='data.json'):
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                self.old = json.load(f)
                self.tmp = self.old['data']
                self.new = self.data
                self.tmp.append(self.new)

            with open(file_name, 'w') as f:
                json.dump(self.old, f, indent=2)

        else:
            json_file = {'data': [self.data]}
            with open(file_name, 'w') as f:
                json.dump(json_file, f, indent=2)
