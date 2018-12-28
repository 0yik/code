# -*- coding: utf-8 -*-
{
    'name': 'POS User Access',
    'version': '1.0',
    'summary': """User Access to Closing POS, Order Deletion, Order Line Deletion,
                  Discount Application, Order Payment, Price Change and Decreasing Quantity""",
    'description': """
POS Manager Validation
======================

This module allows restrictions on some features in POS UI if the cashier has no access rights

Per Point of Sale, you can define access/restriction for the following features:
* POS Closing
* Order Deletion
* Order Line Deletion
* Discount Application
* Order Payment
* Price Change
* Decresing Quantity


Compatibility
-------------

This module is compatible and tested with these modules:
* Restaurant module (pos_restaurant)


Support
-------

Email: macvillamar@live.com


Keywords: Odoo POS validation, Odoo POS validate, Odoo POS confirmation, Odoo POS confirm,
Odoo POS checking, Odoo POS check, Odoo POS access, Odoo POS user, user access, access right,
delete order, delete order line, POS closing, closing POS, decrease quantity
""",
    'category': 'Point of Sale',
    'author': 'MAC5',
    'contributors': ['Michael Aldrin C. Villamar'],
    'website': 'https://apps.odoo.com/apps/modules/browse?author=MAC5',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/pos_user_access_templates.xml',
        'views/res_users_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/user_pos_access_ui.png'],
    'price': 24.99,
    'currency': 'EUR',
}
