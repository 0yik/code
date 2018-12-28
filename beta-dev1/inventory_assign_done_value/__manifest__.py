# -*- coding: utf-8 -*-
{
    'name': "inventory_assign_done_value",

    'summary': """
        Button for assign Done value in All Transfer.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HashMicro/Luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','pdp_stock_inventory_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}