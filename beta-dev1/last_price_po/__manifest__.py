# -*- coding: utf-8 -*-
{
    'name': 'Last Purchase Price',
    'version': '1.0',
    'category': 'Purchase',
    'author': 'HashMicro/ MPTechnolabs - Purvi Pandya',
    'website': "http://www.hashmicro.com",
    'summary': 'It calculates the Last Purchase unit price and Last Average Unit price for each product line in Purchase',
    'depends': [
        'purchase',
    ],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
