# -*- coding: utf-8 -*-
{
    'name': "Hilti User Groups",

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
    'depends': ['base','website'],

    # always loaded
    'data': [
        'security/hilti_user_groups.xml',
        'views/website.xml'
    ],
    # only loaded in demonstration mode
}