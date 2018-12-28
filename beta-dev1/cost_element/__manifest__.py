# -*- coding: utf-8 -*-
{
    'name': "Cost Element",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'project',
        'account',
        'sale',
        'analytic',
        'purchase',
        'purchase_request',
        'sales_team',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/cost_element_views.xml',
        'views/cost_element_extends_views.xml',
        'report/cost_element_report_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
