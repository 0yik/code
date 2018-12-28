# -*- coding: utf-8 -*-
{
    'name': "Grade Point System",

    'summary': """
        Added fields in Sales Order Form
    """,
    'description': """
    """,

    'author': "HashMicro / Bhavin",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'School',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['school','exam','school_attendance','school_assignment_ems','timetable'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'data/view_result_scheduler.xml',
        'views/subject_subject_view.xml',
        'views/grade_master_view.xml',
        'views/view_result_view.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}
