# -*- coding: utf-8 -*-
{
    'name': "Invoice printout for EMS",

    'summary': """
        Invoice printout for EMS on Pergas""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],

    # always loaded
    'data': [
        'report/invoice_fee_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}