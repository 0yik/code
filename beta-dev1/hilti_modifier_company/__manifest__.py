# -*- coding: utf-8 -*-
{
    'name': "hilti_modifier_company",

    'summary': """
        Company configuration and project and booking management""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HILTI/Nitin",
    'website': "http://www.hilti.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Partner-Company',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'hilti_modifier_accessrights', 'zone_and_postal_code_configuration'],

    # always loaded
    'data': [
        'security/hilti_modifier_company.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/project_approvel_email_templates.xml',
        'views/res_partner_views.xml',
        'views/project_and_booking_view.xml',
        'views/customer_booking_admin_view.xml',
        'views/project_menu_admin_view.xml',
        'views/zone_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    # only loaded in demonstration mode
}