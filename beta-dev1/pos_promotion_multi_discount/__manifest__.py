# -*- coding: utf-8 -*-
{
    'name': "pos_promotion_multi_discount",

    'summary': """
        Extention for pos promotion which add multi discount functionality""",

    'description': """
        LExtention for pos promotion which add multi discount functionality
    """,

    'author': "Linescripts / Rajnish",
    'website': "http://www.linescripts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','pos_promotion_multiselect'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}