# -*- coding: utf-8 -*-
{
        'name': "product_price_range",

    'description': """
        Product Price Range
    """,

    'author': "HashMicro / Vaibhav",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',
   # 'installable':False,
    # any module necessary for this one to work correctly
    'depends': [
        'product',
        'sale',
        'credit_debit_note',
        'point_of_sale',
    ],

    # always loaded
    'data': [
      
        'views/product_price_range.xml',
        'views/debit_credit_note.xml',
        'static/src/xml/product_price_range.xml'

    ],
    # only loaded in demonstration mode
    'demo': [

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
