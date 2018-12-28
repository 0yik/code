# -*- coding: utf-8 -*-
{
    'name': 'Project Portal Hm',
    'version': '1.0',
    'category': 'Project Portal Hm',
    'sequence': 1,
    'summary': 'Portal Hm changes required for Project Portal Hm',
    'description': "This module includes Portal Hm setup and changes required for Project Portal Hm",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro / Nikunj',
    'depends': ['project','developer_task','calendar'],
    'data': [
            'data/project_data.xml',
            'views/project_view.xml',
            'views/project_team.xml',
            'security/groups_and_rules.xml',
            'security/ir.model.access.csv',            
            'views/project_templates.xml',
            'views/module_repository.xml',
    ],
    'qweb' : [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}