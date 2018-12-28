# -*- coding: utf-8 -*-
{
    'name': "pos_discount_total_hm",

    'summary': """
        Make discount total for the point of sale""",

    'description': """
        User can enter Discount amount and systems will deduct the Discount Amount from “Total after Taxes” at POS
    """,

    'author': "Hashmicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_discount_total_templates.xml',
        'views/pos_order_modifier_views.xml',
    ],
    'qweb': ['static/src/xml/discount.xml'],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OEEL-1',
}