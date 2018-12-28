# -*- coding: utf-8 -*-
{
    'name': 'Hr Organization Chart',
    'version': '1.0',
    'category': 'HR',
    'author': 'HashMicro/ Sang',
    'website': 'www.hashmicro.com',
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'web',
        'website',
        'hr_dashboard'
    ],
    'data': [
        # ============================================================
        # SECURITY SETTING - GROUP - PROFILE
        # ============================================================
        # 'security/',

        # ============================================================
        # DATA
        # ============================================================
        # 'data/',

        # ============================================================
        # VIEWS
        # ============================================================
        # 'views/',
        'views/hr_employee_view.xml',
        'views/webclient_templates.xml',

        # ============================================================
        # MENU
        # ============================================================
        # 'menu/',

        # ============================================================
        # FUNCTION USED TO UPDATE DATA LIKE POST OBJECT
        # ============================================================
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
