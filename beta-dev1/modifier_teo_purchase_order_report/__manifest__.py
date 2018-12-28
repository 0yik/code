# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Purchase Order Report",

    'summary': """
        Purchase Order Report with Customized View
    """,
    'description': """
    """,

    'author': "Hashmicro / MpTechnolabs - Bhavin Jethva",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'purchase',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['modifier_teo_purchase_order'],

    # always loaded
    'data': [
        'report_menu.xml',
        'wizard/po_fabric_wizard.xml',
        'report/po_fabric_report.xml',
        'report/purchase_order_report.xml',
        'report/general_po_report.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}