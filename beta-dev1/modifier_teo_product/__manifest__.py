# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Product",

    'summary': """
        Added fields in Products Form
    """,
    'description': """
    """,

    'author': "HashMicro / Bhavin",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'product',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['product','stock','purchase'],

    # always loaded
    'data': [
        'views/product_view.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}