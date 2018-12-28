# -*- coding: utf-8 -*-
{
    "name": "Scrap Approval Workflow",
    "author": "HashMicro/ GYBITSolutions / Anand",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "description": "To create new menu and function to manage manufacture scrap own by Bevananda",
    "depends": ["mrp", "stock", "hr", "labor_manufacturing_view"],
    "data": [
        'security/ir.model.access.csv',
        'views/scrap_manufacturing_views.xml',
        'views/machine_management_view.xml',
        'data/stock_manufacturing_data.xml',
    ],
    'demo': [
    ],
    "installable": True,
    'application': True,
}
