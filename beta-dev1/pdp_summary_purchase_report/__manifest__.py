# -*- coding: utf-8 -*-
{
    'name': 'PDP Summary Purchase Report',
    'version': '1.0',
    'category': 'Purchase',
    'sequence': 19,
    'summary': 'setup for summary purchase report.',
    'description': "This module includes summary report for purchase order.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Kannan',
    'depends': ['percentage_incoming_product','PDP_modifier_Product','inventory_on_purchase','pdp_modifier_vendor'],
    'data': [
        'wizard/summary_report_wizard.xml',
        'report/purchase_summary_report_pdf.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}