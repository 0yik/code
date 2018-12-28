# -*- coding: utf-8 -*-
{
    'name': 'Project Leave approve hierarchy for engineer',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 13,
    'summary': 'Project Leave approve hierarchy for engineer',
    'description': "This mudule will add engineed to manage leave approval for engineer, it will jump to leave approving hierarchy to finish the approval.",
    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'depends': [
        'hr', 'propell_project', 'propell_project_leave',
    ],
    'data': [
        'views/project_leave_engineer.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}