# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "brand_sales_report",

    'summary': """
        Modify Sales report can see per brand in the POS.""",

    'description': """
Modify Sales report can see per brand in the POS.
    """,

    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'category': 'Point Of Sale',
    'version': '1.0',
    'depends': ['point_of_sale', 'purchase', 'branch'],
    'data': [
        'views/point_of_sale.xml',
        'views/brand_sales_report.xml',
        'security/ir.model.access.csv',
    ],
#     'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
}
