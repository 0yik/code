# -*- coding: utf-8 -*-

{
    'name' : 'MGM Work Order',
    'version' : '1.0',
    'category': 'sale',
    'author': 'HashMicro / Mareeswaran',
    'description': """Create the work order from sale order. Trace the workorders. Create invoices for completed workorders.""",
    'website': 'www.hashmicro.com',
    'depends' : ['sale', 'stock_account'],
    'data': [
        "data/work_order_data.xml",
        'view/sale_view.xml',
        'view/product_view.xml',
        'view/stock_picking_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
