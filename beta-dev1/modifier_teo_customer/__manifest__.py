# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Customer",

    'summary': """
        Added fields in Customer Form
    """,
    'description': """
        Added below fields in Customer Form,
        a. Tax ID: dropdown list
        b. Currency ID: dropdown list
        c. Sales Term: dropdown list
        d. Category (for Dept): dropdown list
    """,

    'author': "HashMicro / Bhavin",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'base',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','crm','hr', 'sg_account_report'],

    # always loaded
    'data': [
        'views/res_partner_view.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}