# -*- coding: utf-8 -*-
{
    'name': "hm_sales_standardization",

    'summary': """
        Add Sales Target for Sales Team""",

    'description': """
        Add Sales Target for Sales Team
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hasmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sales_team_views.xml',
        'views/sales_target_template.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    'demo': [
    ],
}