# -*- coding: utf-8 -*-
{
    'name': "Leave Auto Allocation Indonesia",
    'description': """
        Leave Auto Allocation Data for Indonesia
    """,
    'author': "HashMicro/ MPTechnolabs(Chankya)",
    'website': "http://www.hashmicro.com",

    'category': 'hr',
    'version': '1.0',
    'depends': ['leave_auto_allocation'],
    # always loaded
    'data': [
        'data/leaves_data.xml',
        'views/sg_leave_extended_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}