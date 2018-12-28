# -*- coding: utf-8 -*-
{
    'name': "ismaya_payment_modfier",

    'summary': """Add PPH Boolean on Register Payment Form""",

    'description': """
        Add PPH Boolean on Register Payment Form
    """,

    'author': "Hashmicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/register_payment_views.xml',
    ],
}