# -*- coding: utf-8 -*-
{
    'name': "project_task_status",

    'summary': """
        Project Task Status""",

    'description': """
        Project Task Status
    """,

    'author': "HashMicro / Duy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'project'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/project_task_view.xml',
        # 'views/mrp_production_view.xml',
    ],
    'demo': [
    ],
}