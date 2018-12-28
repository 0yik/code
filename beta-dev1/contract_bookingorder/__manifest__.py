# -*- coding: utf-8 -*-
{
    'name': "Biocare Contract Modifier",

    'summary': """
        Created Booking order automatically on the basis of type selected
    in contract""",

    'description': """
        Created BO on the basis of type selected in contract.
    """,

    'author': "HashMicro /Krupesh Laiya",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Contract',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stable_account_analytic_analysis',],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        "views/account_analytic_cron.xml",
        'views/account_analytic_analysis_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
