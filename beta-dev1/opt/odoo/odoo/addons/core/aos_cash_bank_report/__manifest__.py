# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cash and Bank Report XLS',
    'version' : '10.0.0.1',
    'license': 'AGPL-3',
    'summary': 'Cash and Bank Report',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
        This module is aim to add cash and bank xls
    """,
    'category' : 'Accounting',
    'website': 'https://www.alphasoft.co.id/',
    'images' : ['static/description/main_screenshot.png'],
    'depends' : ['account'],
    'data': [
        'wizard/cashbank_report_view.xml',
    ],
    'demo': [
        
    ],
    'qweb': [
        
    ],
    'price': 75.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
}
