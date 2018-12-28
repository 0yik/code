# -*- coding: utf-8 -*-
{
    'name': "aikchin_modifier_leave_approval",

    'summary': """
        Aik Chin Leave Approval""",

    'description': """
        Aik Chin Leave Approval
    """,

    'author': "Hashmicro / Duy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','project','hr_holidays','sg_hr_holiday'],
    # always loaded
    'data': [

        'views/human_resource.xml',

    ],
    # only loaded in demonstration mode
}