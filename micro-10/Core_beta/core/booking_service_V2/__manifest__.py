# -*- coding: utf-8 -*-
{
    'name': "Booking Service V2",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "HashMicro / Sang/ luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.2',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'calendar',
        'hr',
        'stock',
        'sale',
        'account',
        'sale_stock',
    ],

    # always loaded
    'data': [
        'security/base_security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/booking_service.xml',
        'views/product_view.xml',
        'views/stock_picking_views.xml',
        'views/list_equipment_view.xml',
        'views/setting_views.xml',
        'views/booking_team_views.xml',
        'views/calendar_views.xml',
        'wizard/work_order_wizard_views.xml',
        'wizard/booking_order_wizard_views.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
