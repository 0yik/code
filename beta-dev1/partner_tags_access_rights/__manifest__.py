# -*- coding: utf-8 -*-
{
    'name': "partner_tags_access_rights",
    'description': """
        Use the partner tags to restrict user access right for customer and vendor database.
    """,

    'author': 'HashMicro / MP technolabs / Monali',
    'website': "http://www.hashmicro.com",
    'category': 'Partner Tags',
    'version': '1.0',
    'depends': ['base'],
    'data': [
	'views/partner_view.xml',
	'views/res_users_view.xml',
    ],
}
