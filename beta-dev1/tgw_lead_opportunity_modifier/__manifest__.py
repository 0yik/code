# -*- coding: utf-8 -*-
{
    "name": "TGW Lead-Opportunity Modifier",
    "author": "HashMicro/ Amit Patel",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "category": "CRM",
    # "depends": ["crm",'hr','sale_crm','opportunity_partner','modifier_tgw_customer'],
    "depends": ["crm",'hr','sale_crm','modifier_tgw_customer'],
    "data": [
        "view/crm_lead_view.xml",
        "view/wedding_details_view.xml",
    ],
    'description':''' Lead-Opportunity Customization for the The Gown Warehouse ''',
    'demo': [],
    "installable": True,
    "auto_install": False,
    "application": True,
}
