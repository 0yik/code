# -*- coding: utf-8 -*-
{
    'name': "Meeting gps",
    'summary': """
        Meeting gps""",
    'description': """
        Meeting gps
    """,
    'author': "HashMicro / MpTechnolabs - Bipin Prajapati",
    'website': "http://www.hashmicro.com",
    'category': 'HashMicro',
    'version': '1.0',
    'depends': [
        'event','calendar','web','partner_geo_map_location',
    ],
    # always loaded
    'data': [
        'templates/assets.xml',
        'views/calendar_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
