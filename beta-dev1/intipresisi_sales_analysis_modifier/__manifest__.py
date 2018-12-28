# -*- coding: utf-8 -*-
{
    'name': "intipresisi_sales_analysis_modifier",

    'summary': """
        Modify sales analysis export""",

    'description': """
        remove double amount in sales analysis export
    """,

    'author': "Hashmicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}