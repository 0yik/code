# -*- coding: utf-8 -*-
{
    'name': "TEO Customer Bank Charges",

    'summary': """
        Customer Bank charges
    """,
    'description': """
    """,

    'author': 'HashMicro / MP technolabs / Monali',
    'website': "www.hashmicro.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': ['sg_partner_payment'],

    'data': [
	"views/receipt_payment_view.xml",
    ],
    'installable': True,
}
