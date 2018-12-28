# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Merging Stock Transfer with SKU Report',
    'version': '1.0.1',
    'category': 'Stock',
    'sequence': 20,
    'summary': 'Merging stock Transfer',
    'description': """
    """,
    'depends': ['stock'],
    'data': [
        'report/report_stock_picking_new.xml',
        'report/stock_report_views.xml',
        'views/stock_view.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'qweb': [],
    'website': '',
}
