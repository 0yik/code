# -*- coding: utf-8 -*-
{
    'name': "Biocare Vehicle Configuration",

    'summary': """
    Configurations for Vehicle Management
    """,

    'description': """
    To create rough draft for configurations base don the discussed requirements
    """,

    'author': "Hashmicro / Krupesh",
    'website': "https://hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'booking_service_V2',
                'sales_team', 'biocare_field_modifier'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_config_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
