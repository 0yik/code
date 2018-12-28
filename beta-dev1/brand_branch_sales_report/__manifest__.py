# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "brand_branch_sales_report",

    'summary': """
        Modify Sales report can see per brand and branch in the POS.""",

    'description': """
Modify Sales report can see per brand and branch in the POS.
    """,

    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'category': 'Point Of Sale',
    'version': '1.0',
    'depends': ['point_of_sale', 'purchase', 'brand_sales_report', 'branch_sales_report'],
    'data': [
        'views/brand_branch_sales_report.xml',
    ],
#     'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
}
