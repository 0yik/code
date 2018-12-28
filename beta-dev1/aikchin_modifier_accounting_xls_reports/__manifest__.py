# -*- coding: utf-8 -*-
{
    'name': "Accouting_xls_report_modifier",

    'summary': """
        Make XLS Theme default = Theme 1""",

    'description': """
        make XLS Theme default = Theme 1
    """,

    'author': "HashMicro /MP technolabs(Chankya)",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','accounting_xls_reports'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
