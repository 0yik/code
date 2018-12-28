# -*- encoding: utf-8 -*-
###########################################################################
#
#    Copyright (C) 2016 - Almighty Consulting Services. <http://www.almightycs.com>
#
#    @author Turkesh Patel <turkesh4friends@gmail.com>
###########################################################################

{ 
    'name': 'Project Issue Start Stop',
    'version': '1.0',
    'author' : 'Almighty Consulting Services',
    'website' : 'http://www.almightycs.com',
    'summary': """Project Issue Start Stop improvements to Simplify project Issue Usability""",
    'description': """Project Issue Start Stop improvements to Simplify project Issue Usability
    Improve Project Issue
    Project issue improvement
    Simplify project Issue
    Issue Timesheet
    Issue Automization
    Automatic Timesheet Entry
    """,
    'depends': ['project', 'project_issue_sheet'],
    'category': 'Project Management',
    'data': [
        'views/project_view.xml',
        'views/project_template.xml',
    ],
    'images': [
        'static/description/issue_start_stop_kanban_almightycs.png',
    ],
    'installable': True,
    'auto_install': False,
    'price': 35,
    'currency': 'EUR',
}
