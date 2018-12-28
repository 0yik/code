# -*- coding: utf-8 -*-
{
    'name': "bevananda_modifier_customer_deposit",
    'description': """
        Create new field in customer deposit main form view
    """,

    'author': "HashMicro / Hoang",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account_deposit'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/customer_deposit.xml',
    ],
}