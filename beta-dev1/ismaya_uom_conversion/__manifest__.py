# -*- coding: utf-8 -*-
{
    'name': "ismaya_uom_conversion",

    'summary': """Change and Conversion BoM from Purchasing and Sales Order""",

    'description': """
        Change and Conversion BoM from Purchasing and Sales Order
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'stock',
        'purchase',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_modifier_views.xml',
    ],
}