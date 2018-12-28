# -*- coding: utf-8 -*-
{
    'name': "Arkco Modifier Products",

    'summary': """
        To create products depend on PT. Arkco specification, where each product will have NUP price and Booking Price differently""",

    'description': """
        To create products depend on PT. Arkco specification, where each product will have NUP price and Booking Price differently
    """,

    'author': "Rajnish",
    'website': "http://www.linescripts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}