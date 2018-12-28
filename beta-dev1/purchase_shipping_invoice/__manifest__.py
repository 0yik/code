# -*- coding: utf-8 -*-

{
    'name' : 'Shipping Invoice',
    'version' : '1.0',
    'category': 'Purchase',
    'author': 'HashMicro / Mareeswaran',
    'description': """Create Shipping Invoice.""",
    'website': 'www.hashmicro.com',
    'depends' : ['purchase'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/purchase_shipping_invoice_view.xml",
        "view/account_invoice_view.xml",
        "view/purchase_view.xml",
        "view/res_config_views.xml",

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
