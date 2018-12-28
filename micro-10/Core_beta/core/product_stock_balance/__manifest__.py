# -*- coding: utf-8 -*-
{
    'name': 'Stocks by Locations',
    'version': '1.1',
    'category': 'Warehouse',
    'summary': 'Inventory level by internal locations right on a product form',
    'description': '''
The app goal is to provide you with instant outlook of how many units of this product are stocked and planned to be at which internal location.
The estimation is provided right on a product form (the tab Inventory) as a table, where each line represents an internal location
All the quants are taken into account, and you get an overview of quantity on hand, incoming and outcoming quantities, forecast quantity
The data and all the parameters are visible both on a specific product variant and on a product template (by all implied variants) form
The default warehouse is presented in user preferences and warehouse in sales order is taken from user settings.
All product quantity measures are represented considering default warehouse.
    ''',
    'price': '44.00',
    'currency': 'EUR',
    'auto_install': False,
    'application':True,
    'author': 'IT Libertas',
    'website': 'https://odootools.com',
    'depends': [
        'product',
        'stock',
        'sale',
    ],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/res_users_view.xml',
    ],
    'qweb': [

    ],
    'js': [

    ],
    'demo': [

    ],
    'test': [

    ],
    'license': 'Other proprietary',
    'images': ['static/description/main.png'],
    'update_xml': [],
    'application':True,
    'installable': True,
    'private_category':False,
    'external_dependencies': {
    },

}
