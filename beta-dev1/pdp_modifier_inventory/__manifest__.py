# -*- coding: utf-8 -*-
{
    'name': "PDP Modifier Inventory",
    'summary': """
        Modifier Inventory""",
    'description': """
        Modifier Inventory
    """,
    'author': "HashMicro / Quy",
    'website': "www.hashmicro.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'sale', 'pdp_stock_inventory_request', 'stock',
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/shipper_view.xml',
        'views/driver_view.xml',
        'views/sale_order_view.xml',
        'views/stock_reordering_rule.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_picking_view.xml',
        'views/template.xml',
        'views/inventory_request.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
