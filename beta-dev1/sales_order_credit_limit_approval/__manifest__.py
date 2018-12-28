# -*- coding: utf-8 -*-
{
    'name' : 'sales_order_credit_limit_approval',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """create approval feature for quotation based on credit limit
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','partner_credit_limit'],
    'data': [
		'view/views.xml',
    ],
}
