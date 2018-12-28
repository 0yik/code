# -*- coding: utf-8 -*-
{
    'name': "quality_control_approval",

    'summary': """
       Modifier Quality Approval""",

    'description': """
       Modifier Quality Approval
    """,

    'author': "HashMicro/ Duy",
    'website': "https://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'quality_control', 'quality_control_stock'],

    # always loaded
    'data': [
        'views/qc_inspection.xml',
    ],
    # only loaded in demonstration mode

}