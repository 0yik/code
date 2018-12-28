# -*- coding: utf-8 -*-
{
    'name': "Mass Mailing Multiprocess",

    'description': """
        Mass Mailing Multiprocess
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Mail',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mass_mailing',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mailing_queue_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
