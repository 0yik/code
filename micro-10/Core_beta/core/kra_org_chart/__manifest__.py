# -*- coding: utf-8 -*-
{
    'name': 'KRA Org. Chart',
    'version': '1.0',
    'description':"""
        The purpose of this enhancement is to link KRA module with the organization chart module. And this will affect selection of manager or subordinate available in the dropdown list.
    """,
    'category': 'HR',
    'author': 'HashMicro/ MPTechnolabs(Chankya)',
    'website': 'www.hashmicro.com',
    'depends': [
        'employee_kra',
    ],
    'data': [
        'views/kra_view.xml'
    ],
    'demo': [],
    'installable': True,
    'active': False,
    'application': True,
}
