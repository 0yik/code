# -*- coding: utf-8 -*-
# Part of eComBucket. See LICENSE file for full copyright and licensing details
{
    'name': "Sale Order Apporval",
    'category': 'Sale',
    'author': "eComBucket",
    'version': '0.1',
    'maintainer': 'support@ecombucket.zohosupport.com',
    'website':'https://twitter.com/ecombucket',
    'depends': ['sale_margin'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
	'currency': 'EUR',
	'images': ['static/description/Banner.png'],
	'pre_init_hook': 'odoo_version_check',
	'installable': True,
	'application': True,
}
