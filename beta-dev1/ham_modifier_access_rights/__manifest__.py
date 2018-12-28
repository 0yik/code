# -*- coding: utf-8 -*-
{
    'name': "ham_modifier_access_rights",

    'summary': """
        Access rights group for Operations, Project Manager and Accounts""",

    'description': """
        Access rights group for Operations, Project Manager and Accounts
    """,

    'author': "Hashmicro/Nitin",
    'website': "http://www.hashmicro.com",

    'category': 'Access Rights',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sales_team', 'account', 'crm', 'project','purchase'],

    # always loaded
    'data': [
        'security/project_task_security.xml',
        'views/project_task_views.xml',
    ],
}
