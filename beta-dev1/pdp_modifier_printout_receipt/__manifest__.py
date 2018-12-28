# -*- coding: utf-8 -*-
{
    'name' : 'Pdp Modifier Printout Receipt',
    'version' : '1.0',
    'category': 'pos',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'description': """Print Outs POS
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
	'point_of_sale','branch',
    ],
    'data': [
        'views/template.xml',
    ],
    'demo': [
    ],
    'qweb': ["static/src/xml/pos_print_receipt.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}
