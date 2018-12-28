# -*- coding: utf-8 -*-
{
    'name': "Hilti My Profile",

    'summary': """
        User Profile""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HILTI/Mustufa",
    'website': "http://www.hilti.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Partner-Company',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hilti_modifier_customer_booking', 'hilti_modifier_accessrights'],

    # always loaded
    'data': [
         'wizard/tester_wizard_views.xml',
        'views/template.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
}