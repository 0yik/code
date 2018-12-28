# -*- coding: utf-8 -*-
{
    'name': "branch_sales_report",

    'summary': """
        sales, branch""",

    'description': """
        Modify report
    """,

    'author': "HashMicro /Luc/ MP Technolabs-Purvi",
    'website': "http://www.hashMicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale', 'point_of_sale', 'branch'],

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