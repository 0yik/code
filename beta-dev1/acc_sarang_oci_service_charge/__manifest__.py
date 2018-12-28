# -*- coding: utf-8 -*-
{
    'name' : 'Account Sarang OCI Service Charge',
    'version' : '1.0',
    'category': 'Accounting',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """Account Sarang OCI Service Charge.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
		'view/service_charge_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
