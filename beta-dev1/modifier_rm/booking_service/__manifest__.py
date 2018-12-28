# -*- coding: utf-8 -*-

{
    'name': 'Booking Service',
    'version': '10.0',
    'author': 'Nilesh Sheliya',
    'category': 'Extra Tools',
    'depends': [
        'hr','sale_stock','calendar'
        ],
    'description': """
With this module, you will be able to Book the event.

""",
    'website': '',
    'data': [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/booking_team_view.xml",
        "views/calendar_event_view.xml",
        "views/hr_employee_view.xml",
        "views/product_template_view.xml",
        "views/sale_order_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_production_lot_view.xml",
        "wizard/warning_wizard.xml",
        ],
    'installable': True,
    'license': 'AGPL-3',
    'application': True,
}
