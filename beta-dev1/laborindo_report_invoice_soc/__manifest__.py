# -*- coding: utf-8 -*-
{
    'name': "laborindo_report_invoice_soc",

    'description': """
       Invoice Report
    """,

    'author': "Hashmicro / MpTechnolabs - Prakash Nanda",
    'website': "http://www.mptechnolabs.com/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','vit_efaktur'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}