# -*- encoding: utf-8 -*-
###########################################################################
#
#    Copyright (C) 2016 - Today Turkesh Patel. <http://www.almightycs.com>
#
#    @author Turkesh Patel <info@almightycs.com>
###########################################################################

{
    'name': 'Project Invoice Withholding or Retainage Management',
    'category': 'Accounting',
    'version': '1.0',
    'author' : 'Almighty Consulting Services',
    'website' : 'http://turkehpatel.odoo.com',
    'summary': """Invoice Withholding management for Projects or Retainage Management.""",
    'description': """Invoice Withholding management for Projects or Retainage Management.
    Withholding Invoice
    Withholding
    Withholding Project Management
    Withholding amount
    Retainage in invoice
    Retainage
    Retainage on project
    """,
    'depends': ['account', 'project'],
    'data': [
        'views/withholding_view.xml',
        'views/res_config_view.xml',
        'wizard/create_withholding_invoice_view.xml',
    ],
    'images': [
        'static/description/withholding_cover.png',
    ],
    'installable': True,
    'price': 49,
    'currency': 'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
