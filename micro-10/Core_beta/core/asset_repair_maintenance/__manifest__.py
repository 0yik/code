# -*- coding: utf-8 -*-
{
    'name': "asset_repair_maintenance",

    'summary': """
        Modify the fields""",

    'description': """
        Modify the fields.
    """,

    'author': "HashMicro / MPTechnolabs - Dhaval",
    'website': "http://www.hashmicro.com",

    'category': 'MRP',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_asset', 'maintenance', 'mrp_repair'],

    # always loaded
    'data': [
        'views/maintenance_views.xml',
        'views/mrp_repair_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
