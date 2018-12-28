# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'City field in branch and POS Order Report',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'City field in branch. POS Order Report have one more option, city',
    'description': """
    """,
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro / Nikunj',
    'depends': ['branch','brand_sales_report','branch_sales_report'],
    'data': [
             'security/ir.model.access.csv',
             'view/branch_view.xml',
             ],
    'auto_install': True,
}
