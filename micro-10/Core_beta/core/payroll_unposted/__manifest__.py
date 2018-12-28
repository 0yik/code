# -*- coding: utf-8 -*-
{
    'name': "Payroll Unposted",

    'summary': """
        This Module keep the journal unposted for payroll in done state""",

    'description': """
       This Module keep the journal unposted for payroll in done state
    """,

    'author': "Teksys Enterprises Pvt. Ltd.",
    'website': "http://www.teksys.in",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll_account','account'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
}