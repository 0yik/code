# -*- coding: utf-8 -*-
{
    "name": "DZH Modifier Fields",
    "author": "HashMicro / Vivek / Sang / GeminateCS",
    "version": "10.0.2",
    "website": "www.hashmicro.com",
    "category": "Sales",
    "depends": ['base','crm', 'product',
                'account','mail','sale_crm'],
    "data": [
            'views/hide_menu.xml',
            'data/sequence.xml',
            'views/crm_lead_view.xml',
            'views/res_partner_view.xml',
            'views/dzh_customer_invoice.xml',
            'views/sale_order_view.xml',
            'security/ir.model.access.csv',
            'views/res_user_view.xml',
    ],
    'description': '''
    ''',
    'demo': [],
    "installable": True,
    "auto_install": False,
}
