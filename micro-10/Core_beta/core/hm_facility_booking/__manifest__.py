# -*- coding: utf-8 -*-
{
    "name": """HM Facility Booking""",
    "summary": """equipment is renamed to Facility""",
    "category": "Equipment",
    "images": [],
    "version": "10.0",
    "application": False,

    "author": "Hashmicro /Duy",
    "website": "https://hashmicro.com",
    "license": "AGPL-3",
    "depends": [
        'maintenance', 'website_portal','hm_facility'
    ],
    "data": [
        "wizard/RescheduleBookingOrder.xml",
        "views/equipment_view.xml",
        "views/facility_booking_menu.xml",
        "views/booking_facility_order_tree_view.xml",
        "views/facility_booking_portal_template.xml",
        "views/templates.xml",
    ],

    "auto_install": False,
    'application': True,
    "installable": True,
}
