# -*- coding: utf-8 -*-
{
    'name': "pos_merge_table_order",

    'summary': """
        Merging order/bills between tables from point of sales of restaurant""",

    'description': """
        Merging order/bills between tables from point of sales of restaurant
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'pos_restaurant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    # load Qweb mode
    'qweb':[
        'static/src/xml/merge_table.xml'
    ],
}