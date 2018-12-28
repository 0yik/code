# -*- coding: utf-8 -*-
{
    'name': "bom_routing_management",


    'description': """
        modify Bill Of Material
    """,

    'author': "HashMicro/Vu ",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mrp',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_bom_view.xml',
        'views/mrp_production.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}