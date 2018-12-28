# -*- coding: utf-8 -*-
import urllib
import json
from hashlib import sha256
from hmac import HMAC
from datetime import datetime

from .data_getter_interface import DataGetterInterface

import logging
_logger = logging.getLogger(__name__)


class CA_BOCGetter(DataGetterInterface):
    """Implementation of DataGetterInterface interface
    for Lazada

    """
    # Lazada
    # https://lazada-sellercenter.readme.io/docs

    code = 'lazada'
    name = 'Lazada'

    site_url = 'https://api.sellercenter.lazada.co.id?'

    def get_parameters(self):
        parameters = {
            'UserID': self.app_id,
            'Version': '1.0',
            'Action': 'GetProducts',
            'Filter': 'all',
            'Format': 'JSON',
            'Timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M+0000"),
        }
        api_key = self.app_secret
        concatenated = urllib.urlencode(sorted(parameters.items()))
        parameters['Signature'] = HMAC(bytearray(api_key, 'utf-8'), bytearray(concatenated, 'utf-8'), sha256).hexdigest()
        return parameters

    def parse_products(self, raw):
        products = []
        data = json.loads(raw)
        if data and 'SuccessResponse' in data:
            for item in data['SuccessResponse']['Body']['Products']:
                product = {}
                product['spuid'] = item.get('SPUId')
                product['attributes'] = item['Attributes']
                product['name'] = product['attributes'].get('name', '')
                products.append(product)
        return products

    # Get Products :
    # https://api.sellercenter.lazada.co.id?Action=GetProducts&Filter=all&Format=XML&Timestamp=2017-03-14T04%3A21%3A51%2B00%3A00&UserID=mikrotek%40mikrotek-mdn.com&Version=1.0&Signature=9055695c59b7b58dd410b347df59ca04aaa6c8bfa5be7dc800061a8415f97afa
    def get_products(self):
        parameters = self.get_parameters()
        url = self.site_url + urllib.urlencode(parameters)

        raw = self.get_url(url=url)
        result = self.parse_products(raw)
        return result