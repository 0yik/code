# -*- coding: utf-8 -*-
{
        'name': "Document Superseding",

    'summary': """
        Document Superseding""",

    'description': """
        Document Superseding (Sales Orders, Invoices, Purchase Orders)
    """,

    'author': "HashMicro / Janeesh / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Custom',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_cancel',
        'sale',
        'purchase',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_update_view.xml',
        'wizard/sale_update_view.xml',
        'wizard/purchase_update_view.xml',
        'views/invoice_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: