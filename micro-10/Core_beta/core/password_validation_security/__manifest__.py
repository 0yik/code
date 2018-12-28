# -*- coding: utf-8 -*-
{
    'name': "Password Validation Security",

    'summary': """
        Adding password validation.
        """,

    'description': """
        Adding password validation.
    """,

    'author': "Hashmicro/ Mustufa",
    'website': "https://www.hashmicro.com/",
    'category': 'Login',
    'version': '0.1',
    'depends': ['base_setup', 'auth_signup', 'odoo_web_login'],
    'data': [
        'data/email_template.xml',
        'views/res_users.xml',
        'views/res_config_views.xml',
        'views/templates.xml',
    ],
}
