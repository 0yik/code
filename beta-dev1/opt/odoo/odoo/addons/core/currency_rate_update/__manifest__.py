# -*- coding: utf-8 -*-
{
    'name': "Currency Rate Update",

    'summary': """
        Currency Rate Update""",

    'description': """
        Currency Rate Update
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Financial Management/Configuration',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
    ],

    # always loaded
    'data': [
        'views/service_cron_data.xml',
        'views/currency_rate_update.xml',
        'views/company_view.xml',
        'security/rule.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}