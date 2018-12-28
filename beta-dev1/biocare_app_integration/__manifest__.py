# -*- coding: utf-8 -*-
{
    "name": """Biocare App Integration""",
    "summary": """Biocare app makes Odoo integration with mobile app""",
    "category": "Sales",
    "images": [],
    "version": "10.0",
    "application": False,

    "author": "Hashmicro / Balaji/Soundarya",
    "website": "https://hashmicro.com",
    "license": "AGPL-3",
    "depends": [
        'sale','crm','hr', 'stock', 'booking_service_V2','stock','booking_service_restriction_reusable',
        'zone_and_postal_code_configuration', 'biocare_modifier_services_menu','biocare_field_modifier',
        'hr_timesheet_sheet',
    ],
    "data": [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/res_users_view.xml',
    ],

    "auto_install": False,
    'application': True,
    "installable": True,
}
