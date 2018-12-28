# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'DZH Modifier Fields',
    'version': '1.1',
    'category': 'Crm',
    'summary': 'Custom Crm Phonecall modifier fields',
    'description': """
    """,
    'author': 'HashMicro / GeminateCS',
    'website': 'www.hashmicro.com', 
    'depends': [
        'crm',
        'crm_phonecall',
        'product',
	'dzh_modifier_fields',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_phonecall_view.xml',
        'views/configuration_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
