# -*- coding: utf-8 -*-
{
    'name': "generate_2d_barcode_do",

    'summary': """
        Generate 2D barcode from DO.""",

    'description': """
        Generate the printout for 2D barcode from Delivery Order.
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'warehouse_serializer',
        'admiral_modifier_printout',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/qr_code_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}