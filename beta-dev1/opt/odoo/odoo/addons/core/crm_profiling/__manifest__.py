# -*- coding: utf-8 -*-
{
    'name': "Customer Profiling",

    'summary': """
        Customer Profiling""",

    'description': """
This module allows users to perform segmentation within partners.
=================================================================

It uses the profiles criteria from the earlier segmentation module and improve it.
Thanks to the new concept of questionnaire. You can now regroup questions into a
questionnaire and directly use it on a partner.

It also has been merged with the earlier CRM & SRM segmentation tool because they
were overlapping.

    **Note:** this module is not compatible with the module segmentation, since it's the same which has been renamed.
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Marketing',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account_followup',
        'base',
        'crm',
        'product_pack',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/open_questionnaire_view.xml',
        'views/crm_segmentation_view.xml',
        'views/crm_profiling_view.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/crm_profiling_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}