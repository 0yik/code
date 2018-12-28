# -*- coding: utf-8 -*-

{
    'name': 'Booking Service',
    'version': '10.0',
    'author': 'Nikunj Popat',
    'depends': ['hr','sale_stock','calendar'],
    'website':'simbeez.com',
    'description': """
    You can book human resource as well as equipments. Sale Order will be work as booking order and you can book 
    human resources as well as equipments for specific time period.
""",
    'data': [
        "security/ir.model.access.csv",
        "views/booking_customizations_views.xml",
        "views/team.xml",
        "views/sale_view.xml",
        "wizard/event_overlap_warning.xml",
        ],
    'installable': True,
    'license': 'AGPL-3',
    'application': True,
}
