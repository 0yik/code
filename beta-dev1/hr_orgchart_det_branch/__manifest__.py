# -*- coding: utf-8 -*-
{
    'name': 'Hr Organization Chart DEPT/BRANCH',
    'version': '1.0',
    'category': 'HR',
    'author': 'HashMicro/ Parikshit Vaghasiya',
    'website': 'www.hashmicro.com',
    'license': 'AGPL-3',
    'depends': [
        'web',
        'hr_organization_chart'
    ],
    'data': [
        'views/webclient_templates.xml',
    ],
    'qweb': [
        "static/src/xml/hr_dashboard.xml",
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'active': False,
    'application': True,
}
