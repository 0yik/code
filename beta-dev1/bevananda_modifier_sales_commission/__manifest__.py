# -*- coding: utf-8 -*-
{
    "name": "Bevananda Modifier Sales Commission",
    "author": "Hashmicro/GYB IT SOLUTIONS-Trivedi",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "description":"",
    "category": "sale",
    "depends": ["sale", "sale_commission_target_gt", "hr_timesheet", "hr_attendance",'sales_team','web_readonly_bypass','sale_margin' ],
    "data": [
        'security/ir.model.access.csv',
        'views/commission_quarter_with_details.xml',
        'views/sale_commission_view.xml',
        'views/generate_sales_person.xml',
        'views/sales_person_commision.xml',
    ],
    'demo': [
    ],
    "installable": True,
    'application': True,
}
