# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Sale Order Line Report",

    'summary': """
        Sale Order Line Report with Date Filter Wizard
    """,
    'description': """
    """,

    'author': "Hashmicro / MpTechnolabs - Bhavin Jethva",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['modifier_teo_sale_order'],

    # always loaded
    'data': [
        'report/sale_order_report.xml',
        'report_menu.xml',
        'wizard/sale_order_wizard.xml',
        
    ],
    # only loaded in demonstration mode
    'installable': True,
}