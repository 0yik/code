# -*- coding: utf-8 -*-
{
    "name": """HM Facility""",
    "summary": """equipment is renamed to Facility""",
    "category": "Equipment",
    "images": [],
    "version": "10.0",
    "application": False,

    "author": "Hashmicro / Soundarya - Hashmicro/MPTechnolabs/Bipin Prajapati /Duy",
    "website": "https://hashmicro.com",
    "license": "AGPL-3",
    "depends": [
        'maintenance','helpdesk', 'website_portal',
    ],
    "data": [
        "views/templates.xml",
        "views/helpdesk_portal_template.xml",
        "views/location_view.xml",
        "views/equipment_view.xml",
        "views/helpdesk_ticket_view.xml",
        "views/maintenance_request_view.xml",
        "views/maintenance_view.xml"
    ],

    "auto_install": False,
    'application': True,
    "installable": True,
}
