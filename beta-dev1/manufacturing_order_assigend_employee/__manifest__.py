# -*- coding: utf-8 -*-
{
    "name": "Manufacturing_Order_Assigend_Employee",
    "author": "HashMicro/ GYBITSolutions / Anand",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "description":"To create new module for managing assigned employee for Manufacturing Order.",
    "category": "Manufacturing",
    "depends": ["mrp", "manufacturing_plan", "hr_timesheet", "hr_attendance", ],
    "data": [
        'security/ir.model.access.csv',
        'views/mrp_production_view.xml',
    ],
    'demo': [
    ],
    "installable": True,
    'application': True,
}
