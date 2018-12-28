# -*- coding: utf-8 -*-
{
    'name': 'Project Leave approve hierarchy',
    'version': '1.0',
    'category': 'Leave Management',
    'sequence': 13,
    'summary': 'Project Leave approve hierarchy',
    'description': "This module will give priority to propell_project hierarchy above leave approving hierarchy. Once propell_project hierarchy is done, it will jump to leave approving hierarchy to finish the approval.",
    'website': 'www.mptechnolabs.com',
    'author': 'Bharat Chauhan',
    'depends': [
        'hr', 'propell_project', 'hr_employee_hierarchy'
    ],
    'data': [
        'views/project_leave_approve.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}