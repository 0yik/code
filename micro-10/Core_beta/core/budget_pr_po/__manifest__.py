# -*- coding: utf-8 -*-
{
    "name": "Budget Management - PO",
    "category": 'Purchase',
    'summary': 'Show total budget and remaining budget in Purchase Request and Purchase Order',
    "description": """
        Show total budget value and remaining budget value in Purchase Request and Purchase Order
    """,
    "sequence": 1,
    "author": "HashMicro / Mareeswaran",
    "website": "www.hashmicro.com",
    "version": '1.0',
    "depends": ['budget_management_extension','purchase', 'purchase_request', 'hr_timesheet_invoice', 'internal_purchase_milestones'],
    "data": [
        "views/purchase_view.xml",
        "views/purchase_request_view.xml",

    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
