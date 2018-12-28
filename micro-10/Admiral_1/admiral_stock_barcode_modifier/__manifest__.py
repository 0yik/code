# -*- coding: utf-8 -*-
{
    'name': "admiral_stock_barcode_modifier",

    'description': """
        Modify function on Barcode module
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Barcode',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock_barcode'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}