# -*- coding: utf-8 -*-
{
    'name': "hilti_modifier_loginsignup",

    'summary': """
        Website pages for Login, Register and forgot password """,

    'description': """
    """,

    'author': "Hilti/Nitin",
    'website': "https://www.hilti.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website','auth_signup'],

    # always loaded
    'data': [
        'wizard/customer_verification_wizard.xml',
        'views/res_users_views.xml',
        'views/templates.xml',
    ],
}