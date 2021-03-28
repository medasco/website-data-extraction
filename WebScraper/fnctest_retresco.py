import json
import requests
from requests.auth import HTTPBasicAuth
from http import HTTPStatus

import pytest
import logging
import common.constants

logger = logging.getLogger('test')

gtin = '4007065578969'
base_url = common.constants.URL_CORE_ARTICLE
headers = {
    'channel': common.constants.CHANNEL_NAME_RETRESCO,
    'gtin': gtin,
    'source': None
}
authentication = HTTPBasicAuth('mki', 'mki')


class TestRetrescoPlugin:
    @pytest.fixture(autouse=True)
    def setup(self, load_lambda_module, load_lambda_context):
        self.module_retresco = load_lambda_module(parent_dir='text_engine')
        self.lambda_context = load_lambda_context(function_name='text_engine')

    def test_unclassified_category(self):
        assert self.module_retresco.lambda_handler.__name__ == 'lambda_handler'
        test_payload = {
            'topic': 'articleNew',
            'graceTimeInSec': 60,
            'gtin': gtin,
            'channel': 'gkkCilRetresco',
            'action': '',
            'source': None
        }
        response = self.module_retresco.lambda_handler(test_payload, self.lambda_context)
        assert HTTPStatus.OK == int(response['statusCode'])

    def test_get_retresco_article(self):
        article_lake_response = requests.get(base_url, auth=authentication, headers=headers)
        response = article_lake_response.json()
        assert HTTPStatus.OK == int(response['statusCode']['code'])
        assert 1 == len(response['articles'])
        assert gtin == response['articles'][0]['gtin']
        assert common.constants.CHANNEL_NAME_RETRESCO == response['articles'][0]['channel']
        assert HTTPStatus.OK == int(response['articles'][0]['statusCode']['code'])

    def test_retresco_article_cleanup(self):
        article_lake_response = requests.delete(base_url, auth=authentication, headers=headers)
        response = article_lake_response.json()
        assert HTTPStatus.OK == int(response['statusCode']['code'])

        article_lake_response = requests.get(base_url, auth=authentication, headers=headers)
        response = article_lake_response.json()
        assert HTTPStatus.OK == int(response['statusCode']['code'])
        assert HTTPStatus.NOT_FOUND == int(response['articles'][0]['statusCode']['code'])


if __name__ == '__main__':
    pytest.main([__file__])
