# -*- coding: utf-8 -*-
{
    "name": """Kimhuat App Integration""",
    "summary": """Kimhuat app makes Odoo integration with mobile app""",
    "category": "Sales",
    "images": [],
    "version": "10.0",
    "application": False,

    "author": "Hashmicro / Soundarya",
    "website": "https://hashmicro.com",
    "license": "AGPL-3",
    "depends": [
        'sale','crm','hr', 'stock', 'booking_service_V2','stock','kimhuat_modifier_fields',
        'hr_timesheet_sheet','kimhuat_modifier_access_rights',
    ],
    "data": [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/calendar_view.xml',
    ],

    "auto_install": False,
    'application': True,
    "installable": True,
}
