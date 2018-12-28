# -*- coding: utf-8 -*-
{
    'name' : 'PDP Modifier Sales Report',
    'version' : '1.0',
    'category': 'Sales',
    'author': 'HashMicro / MP technolabs(Chankya)',
    'description': """
        This module will add some reports for sales.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['PDP_modifier_Product','pdp_modifier_sales'],
    'data': [
        'wizard/sale_report_wizard_view.xml',
        'wizard/sale_all_report_wizard_view.xml',
        'report/sale_per_customer_report_templates.xml',
        'report/sale_per_item_report_templates.xml',
        'report/sale_realization_report_templates.xml',
        'report/sale_report_templates.xml',
        'report/sale_report.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
