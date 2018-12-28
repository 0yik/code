# -*- coding: utf-8 -*-
{
    'name': "pdp_modifier_access_right",

    'summary': """
        pdp_modifier_access_right""",

    'description': """
        pdp_modifier_access_right
    """,

    'author': "Hashmicro / Luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sales_team','account','stock','analytic','bi_generic_import'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/access_right_group.xml',
        'views/hide_menu.xml',
        'views/sales.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}