# -*- coding: utf-8 -*-
{
    'name': "add_filter_orders",

    'summary': """
        Filter orders history""",

    'description': """
        Filter orders history base on quantity and time
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'pos_orders', 'pos_order_return'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'views/pos_templates.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}