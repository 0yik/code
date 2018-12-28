# coding=utf-8
{
    'name': "Prospect Customer",
    'description': """
       This module adds menu to get opportunity partner list""",
    'author': "Hashmicro / TechUltra Solutions - Krutarth Patel",
    'website': "http://www.techultrasolutions.com/",

    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/res_partner_modifier.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}