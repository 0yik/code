# -*- coding: utf-8 -*-
{
    'name': "Approving Matrix Configuration",


    'description': """
        Allow users to select the approving user based on the selected Amount range.
    """,

    'author': "HashMicro/MP Technolabs/ vatsal",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','so_blanket_order','purchase',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/approving_matrix_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}