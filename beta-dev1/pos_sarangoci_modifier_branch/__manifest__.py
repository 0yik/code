# -*- coding: utf-8 -*-
{
    'name' : 'pos_sarangoci_modifier_branch',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / MP technolabs / Bipin Prajapati',
    'description': """Edit POS interface.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['pos_analytic_by_config'],
    'data': [
		'view/pos_conf_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
	'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
