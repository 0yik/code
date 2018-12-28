# -*- coding: utf-8 -*-
{
    'name': "My Note",

    'summary': """
Sticky notes, Collaborative, Memos""",

    'description': """
This module allows users to create their own notes inside Odoo
=================================================================

Use notes to write meeting minutes, organize ideas, organize personal todo
lists, etc. Each user manages his own personal Notes. Notes are available to
their authors only, but they can share notes to others users so that several
people can work on the same note in real time. It's very efficient to share
meeting minutes.

Notes can be found in the 'Home' menu.
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'note',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/note_security.xml',
        'views/res_users_views.xml',
        'views/note_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}