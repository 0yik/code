# -*- coding: utf-8 -*-
{
    'name': "mgm_modifer_tax_adjustment",

    'summary': """
        Manual tax adjustment wizard Modifier field.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HashMicro /Luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/make_manual_tax_adjustments.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}