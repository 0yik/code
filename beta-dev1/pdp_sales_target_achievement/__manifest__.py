# -*- coding: utf-8 -*-
{
    'name': "PDP Sales Target & Achivement",
    'summary': """
        Sales Target & Achivement""",
    'description': """
        Sales Target & Achivement
    """,
    'author': "HashMicro / Quy",
    'website': "www.hashmicro.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'crm','sales_team','branch'
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/branch_target_popup_view.xml',
        'views/branch_target_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}