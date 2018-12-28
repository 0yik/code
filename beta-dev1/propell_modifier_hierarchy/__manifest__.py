# -*- coding: utf-8 -*-
{
    'name': "Leave Request Hierarchy",

    'summary': """
        Module Provide Hierarchy to approve leave request for diffrent position   
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Hashmicro / MpTechnolabs - Parikshit Vaghasiya",
    'website': "http://www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','hr','hr_holidays','sg_hr_holiday','access_rights_group'],

    # always loaded
    'data': [
        'security/hr_security_leave.xml',
        'security/ir.model.access.csv',
        'views/leave_modifier_hierarchy_view.xml',
        'views/leave_approval_hierarchy.xml',
        'views/user_leave_group.xml',
        'views/notify_email_template.xml',
    ],

}