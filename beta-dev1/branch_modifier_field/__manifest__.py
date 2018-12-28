# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Branch Fields ext",
    'summary': """Modify Branch Master form.""",
    'description': """Modify Branch Master form.""",

    'website': 'http://www.hashmicro.com/',
    'author': 'HashMicro / GBS',
    'category': 'Branch',
    'version': '1.0',
    'depends': ['branch'],
    'data': [
        'views/branch_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,

}
