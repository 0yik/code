# -*- coding: utf-8 -*-
{
    'name': "purchase_tender_from_contract",

    'description': """
        Auto create purchase tender from contract.
    """,

    'author': "HashMicro / Hoang",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Contract',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stable_account_analytic_analysis',
        'purchase_tender_comparison',
        'purchase_requisition'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/contracts_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}