# -*- coding: utf-8 -*-
{
    'name' : 'Import Product Inventory',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'HashMicro / Mareeswaran',
    'description': 'This module will import products in inventory order line.',
    'website': 'www.hashmicro.com',
    'depends' : ['pdp_stock_inventory_request', 'stock'],
    'data': [
        'wizard/move_line_import_wizard.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
