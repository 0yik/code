# -*- coding: utf-8 -*-
{
    'name': "PPH Receipt",
    'summary': """
    """,
    'description': """
        
    """,
    'author': "HashMicro / Quy",
    'website': "www.hashmicro.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'account',
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/receipt_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}