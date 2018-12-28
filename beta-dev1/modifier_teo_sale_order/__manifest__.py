# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Sale Order",

    'summary': """
        Added fields in Sales Order Form
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
    'depends': ['sale','stock','delivery','project','account','modifier_teo_customer','modifier_teo_accounting'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report_menu.xml',
        'data/data.xml',
        'wizard/vendor_bill_report.xml',
        'wizard/report_download_test.xml',
        'views/sale_order_view.xml',
        'views/sale_order_line_view.xml',
        'views/fabric_fabric_view.xml',
        'views/account_invoice_view.xml',
        'wizard/pre_po_wizard.xml',
        'wizard/so_line_wizard.xml',
        'wizard/create_invoice_wizard.xml',
        'report/pre_po_report.xml',
        'report/so_line_report.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}