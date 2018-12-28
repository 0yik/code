# -*- coding: utf-8 -*-
{
    'name': "Propell Modifier Employee",

    'summary': """
       Employee view changes""",

    'description': """
       New employee form view changes
    """,

    'author': "Hashmicro/ Renuka",
    'website':  "http://www.hashmicro.com",

   
    'category': 'Leave Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_holidays'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/employee_view_changes.xml',
        
    ],
    # only loaded in demonstration mode
    
}