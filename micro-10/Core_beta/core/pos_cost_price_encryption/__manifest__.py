# -*- coding: utf-8 -*-
{
    'name': "pos_cost_price_encryption",

    'summary': """
        Encrypt cost price into alphabets and show it in POS.""",

    'description': """
        Encrypt cost price into alphabets and show it in POS.
    """,

    'author': "HashMicro / Sang / Mustufa",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'point_of_sale', 'pos_cost_price'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_price_templates.xml',
        'views/pos_config.xml',
    ],
    'qweb': ['static/src/xml/product.xml'],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}