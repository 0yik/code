# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'IPT Modifier Fields',
    'version': '1.1',
    'category': 'Sale',
    'summary': 'Custom Sale order report and fields modifier',
    'description': """
    """,
    'author': 'HashMicro / GeminateCS',
    'website': 'www.hashmicro.com', 
    'depends': [
        'sale',
        'product_quotation_customize',
        'quotation_pit_extended_ten',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'report/sale_report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
