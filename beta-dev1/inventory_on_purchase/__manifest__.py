# -*- coding: utf-8 -*-
{
    'name': 'Purchase Invetory View',
    'version': '1.0',
    'category': 'Product',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'description': """
    """,
    'website': 'http://www.hashmicro.com/',
    'depends': [
        'sale', 'sales_team', 'account', 'procurement', 'stock', 'warehouse_modifier_shop', 'purchase',
        'rfq_approval_request',
    ],
    'data': [
        'views/purchase_order.xml',
        'views/template.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'css' : ['static/src/css/custom.css'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
