# -*- coding: utf-8 -*-
{
    "name": "Wasted Management",
    "author": "HashMicro/ GYBITSolutions / Anand",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "description": "To create new menu and function to manage wasted material",
    "depends": ["mrp", "stock", "hr", "scrap_approval_workflow"],
    "data": [
        'security/ir.model.access.csv',
        'views/wasted_management_view.xml',
        'views/workorder_view.xml',
        'views/machine_management_view.xml',
        'data/wasted_management_data.xml',
    ],
    'demo': [
    ],
    "installable": True,
    'application': True,
}
