# -*- coding: utf-8 -*-
{
    'name' : 'Inventory Request Extended',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'HashMicro / MPTechnolabs - Parikshit Vaghasiya',
    'description': """
        -- Module hide fields and add menu on website
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['sarangoci_stock_inventory_request'],
    'data': [
        'data/so_website_menu.xml',
       'views/inventory_request_ext_view.xml'
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
