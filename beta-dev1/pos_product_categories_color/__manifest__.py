# -*- coding: utf-8 -*-
{
    'name': "pos_product_categories_color",

    'summary': """
        can set color per product categories in POS screen.""",

    'description': """
        can set color per product categories in POS screen.
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'POS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_category_views.xml',
        'views/pos_templates.xml',
    ],
    'qweb': [
        'static/src/xml/screens.xml',
    ],
}