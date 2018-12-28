# -*- coding: utf-8 -*-
{
    'name': "pos_so_payments",

    'summary': """
        Payment for sales order that created from POS""",

    'description': """
        Payment for sales order that created from POS
    """,

    'author': "Hashmicro/Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'hr', 'point_of_sale', 'pos_to_sales_order'],

    # always loaded
    'data': [
        'views/pos_templates.xml',
        'views/sales_order_views.xml',
    ],
    # only loaded in demonstration mode
    'qweb': ['static/src/xml/*.xml'],
}