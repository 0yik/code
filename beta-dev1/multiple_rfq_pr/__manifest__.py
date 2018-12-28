# -*- coding: utf-8 -*-
{
    'name': "multiple_rfq_pr",

    'description': """
        Allowing users to attach RFQs to Purchase Request and users to approve and confirm the RFQ
    """,

    'author': "HashMicro/Quy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase_requisition','purchase_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
            'views/purchase_agreement_view.xml',
            'views/purchase_request_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}