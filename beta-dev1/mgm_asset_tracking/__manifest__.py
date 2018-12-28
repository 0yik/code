# -*- coding: utf-8 -*-

{
    'name' : 'MGM Asset Tracking',
    'version' : '1.0',
    'category': 'Accounting',
    'author': 'HashMicro / Mareeswaran',
    'description': """This module to pull asset from the Purchase Order using the vendor bill.""",
    'website': 'www.hashmicro.com',
    'depends' : [
        'account',
        'purchase',
    ],
    'data': [
        'wizard/asset_product_selection_view.xml',
        'view/account_asset_view.xml',
        'view/purchase_order_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
