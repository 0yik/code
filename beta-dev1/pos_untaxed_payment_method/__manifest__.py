# -*- coding: utf-8 -*-
{
    'name' : 'pos_untaxed_payment_method',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Viet',
    'description': """make the search product on pos can be able to do by scan the IMEI barcode
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','point_of_sale','pos_tax_branch'],
    'data': [
		'view/register.xml',
        'view/account_journal.xml'
    ],
    'demo': [
    ],
    'qweb': [
	    'static/src/xml/*.xml',
    ],
}
