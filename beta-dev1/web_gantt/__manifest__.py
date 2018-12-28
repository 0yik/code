# -*- coding: utf-8 -*-
{
    'name': "Web Gantt",

    'summary': """
        OpenERP Web Gantt chart view.""",

    'description': """
OpenERP Web Gantt chart view.
=============================

    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'web',
    ],

    # always loaded
    'data': [
        'views/web_gantt_templates.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    # 'auto_install': True,
}