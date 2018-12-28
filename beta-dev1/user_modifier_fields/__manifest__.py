# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "User Fields ext",
    'summary': """Modify User Master form.""",
    'description': """Modify User Master form.""",

    'website': 'http://www.hashmicro.com/',
    'author': 'HashMicro / GBS',
    'category': 'Base',
    'version': '1.0',
    'depends': ['branch_modifier_field'],
    'data': [
        'views/res_users_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,

}
