# -*- coding: utf-8 -*-
{
    'name': "AP Intervention",

    'summary': """
        Added Functionality for AP Intervention in School System
    """,
    'description': """
    """,

    'author': "HashMicro / Bhavin",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'School',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['school','gos_staff_profile'],

    # always loaded
    'data': [
        'views/define.xml',
        'report_menu.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/email_template_view.xml',
        'views/ap_intervention_view.xml',
        'views/master_list_view.xml',
        'wizard/master_list_wizard.xml',
        'report/master_list_report.xml',
        'wizard/termly_updates_wizard_view.xml',
        'report/termly_updates_report.xml',
        'wizard/report.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}