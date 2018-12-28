# -*- coding: utf-8 -*-
{
    'name': "aikchin_modifier_appraisal_ratings",

    'summary': """
        Create the “Rating Description” field.""",

    'description': """
        Create the “Rating Description” field.
    """,

    'author': "Hashmicro / Luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','employee_appraisal'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_rating_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
