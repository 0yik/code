# -*- coding: utf-8 -*-
{
    'name': 'Invoice pritout Changes',
    'version': '1.0',
    'summary': 'Invoice pritout Changes',
    'description': """
Changed Features
================================
* Change header footer
* Change the contents of report according to CCM requirements
    """,
    'author': 'HashMicro/Kunal',
    'category': 'Invoice',
    'depends': ['pos_rental'],
    'data': [
        'report/report_layout.xml',
        'report/report_invoice.xml',
        'views/custom_invoice_report.xml',
        'views/invoice_view.xml',
    ],
    'installable': True,
}
