# -*- coding: utf-8 -*-
{
    'name' : 'Central Kitchen',
    'version' : '1.0',
    'category': 'Inventory',
    'author': 'HashMicro /Kannan',
    'description': """Stock deduction and production for BOM.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base_setup','product', 'product_expiry', 'account','stock_picking_wave','mrp','portal_sale','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_paperformat.xml',
        'views/lot_barcode_custom.xml',
        'views/report_lot_barcode.xml',
        'views/stock_production_lot_view.xml',
        'views/templates.xml',
        'wizard/product_produce_view.xml',
        'views/product_view.xml',
        'wizard/stock_config_view.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
