# -*- coding: utf-8 -*-
{
    'name': "Matahari Modifier Asset",

    'summary': """
        Matahari Modifier Asset""",

    'description': """
        Matahari Modifier Asset
    """,

    'author': "Hashmicro / Viet",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_asset'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    # only loaded in demonstration mode
}