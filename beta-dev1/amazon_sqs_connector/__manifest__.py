# -*- coding: utf-8 -*-
{
    'name': "Amazon SQS Connector",

    'summary': """
        Connects with Amazon SQS to Send and Recieve Messages""",

    'description': """
        Connects with Amazon SQS to Send and Recieve Messages
    """,

    'author': "Hashmicro / Vinay",
    'website': "http://www.hashmicro.com",

    'category': 'Other',
    'version': '0.1',

    'depends': ['base', 'sale', 'product', 'purchase', 'account', 'stock', 'account_accountant', 'purchase'],

    'data': [
        'security/ir.model.access.csv',
        'views/configuration.xml',
        'views/scheduler.xml',
        'views/product_view.xml',
        'views/sale_order_view.xml',
        'views/shipping_address_view.xml',
        'views/account_invoice_view.xml',
        'views/delivery_order_view.xml',
        'views/supplier_view.xml',
        'views/web_customise.xml',
        'views/stock_move_view.xml',
    ],
}
