# -*- coding: utf-8 -*-
{
    "name": "Labor_Manufacturing_View",
    "author": "HashMicro/ GYBITSolutions / Anand",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "description": "To create new module for managing Labor Manufacturing workers and machine",
    "category": "Manufacturing",
    "depends": ["mrp", "manufacturing_plan", "hr_timesheet", "hr_attendance","manufacturing_order_assigend_employee","report" , "stock"],
    "data": [
        'security/ir.model.access.csv',
        'wizard/mrp_workcenter_block_view.xml',
        'report/report_manufacturing_orders_menu.xml',
        'report/report_manufacturing_orders_template.xml',
        'views/labor_mrp_view.xml',
        'views/hr_employee.xml',
        'views/machine_management_templates.xml',
    ],
    'demo': [
    ],
    "installable": True,
    'application': True,
}
