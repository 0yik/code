# -*- coding: utf-8 -*-
{
    'name' : 'PDP Modifier Purchase Report',
    'version' : '1.0',
    'category': 'purchase',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Trivedi',
    'description': """ This module will add some reports for purchase.
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
	'stock', 'product', 'purchase', 'pdp_summary_purchase_report', 'PDP_modifier_Product', 'pdp_modifier_purchase',
    ],
    'data': [
    'wizard/purchase_report_wizard_view.xml',
    'wizard/purchase_all_report_wizard.xml',
    'report/purchase_report_menus.xml',
    'report/global_purchase_report_templates.xml',
    'report/purchase_per_customer_report_templates.xml',
    'report/purchase_realization_report_templates.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
