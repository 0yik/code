# -*- coding: utf-8 -*-
{
    'name': "analytic_approving_extension",

    'description': """
        Combines both project_manager_approval_pr and approving_matrix_pr together
         -  Additional level of approval for Project Manager before Purchase Request is routed to Purchase Manager to approve
         -  Allow users to select the approving user based on the selected Product Category and Amount range.

    """,

    'author': "HashMicro/Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase_request', 'hr', 'analytic'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/approving_matrix_views.xml',
        'views/purchase_request_views.xml',
        'views/account_analytic_account_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}