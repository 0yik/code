# -*- coding: utf-8 -*-

{
    'name': 'Expiry Tracker',
    'version': '10.0',
    'author': 'Nilesh Sheliya',
    'category': 'Extra Tools',
    'depends': [
        'stock'
        ],
    'description': """
With this module, you will be able to receive the notification regarding the product stock expiry.

""",
    'website': '',
    'data': [
        "security/ir.model.access.csv",
        "data/expiry_data.xml",
        "views/stock_location_view.xml",
        "views/expiring_product_view.xml",
        
        ],
    'installable': True,
    'license': 'AGPL-3',
    'application': True,
}
