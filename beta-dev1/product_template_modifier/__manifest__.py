# -*- coding: utf-8 -*-
{
    'name': "product_template_modifier",

    'summary': """
        product_template_modifier""",

    'description': """
        product_template_modifier
    """,

    'author': "HashMicro / Hoang",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'simple_stock2',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/simple_stock_in_views.xml',
        'views/simple_stock_out_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}