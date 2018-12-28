# -*- coding: utf-8 -*-

{
    'name': 'Developer Task',
    'version': '1.0',
    'summary': 'Developer Task',
    'description': """
        Customizations in Project
    """,
    'author': 'HashMicro / Axcensa / MP Technolabs',
    'website': 'www.hashmicro.com',
    'category': 'Social Network',
    'sequence': 0,
    'depends': ['project','module_repository'],
    'data': [
        'security/record_rules.xml',        
        'security/ir.model.access.csv',
        'views/developer_task.xml',
        'data/data.xml',

    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}
