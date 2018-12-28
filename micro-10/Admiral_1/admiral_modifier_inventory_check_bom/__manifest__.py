# -*- coding: utf-8 -*-
{
    'name': "admiral_modifier_inventory_check_bom",

    'summary': """
        Modify inventory_check_bom module""",

    'description': """
        Modify inventory_check_bom module
    """,

    'author': "Hashmicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',


    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'inventory_check',
        'inventory_check_bom'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_check_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'qweb': ['static/xml/inventory_bom_check.xml'],
}