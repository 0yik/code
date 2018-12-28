# -*- coding: utf-8 -*-
{
    'name' : 'Cooking List',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'HashMicro / Chankya',
    'description': """ Can see cooking list per product variants which wants to be produced.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['mrp','sale'],
    'data': [
        'report/product_reports.xml',
        'report/product_cookinglist_template.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
