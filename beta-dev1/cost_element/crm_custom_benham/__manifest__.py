# -*- coding: utf-8 -*-
{
    'name': "CRM - Benham",

    'summary': """
        Custom CRM Module
        """,

    'description': """
    """,

    'author': "Hashmicro / Arya",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hashmicro',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'crm',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/crm_view.xml',
        'views/partner_view.xml',
        'views/crm_custom_benham_view.xml',
    ],
    'css': ['static/src/css/crm_custom_benham.css',],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}