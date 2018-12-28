# -*- coding: utf-8 -*-
{
    'name': "aikchin_modifier_access_right",

    'summary': """
        Aik Chin Access Right""",

    'description': """
        Aik Chin Access Right
    """,

    'author': "Hashmicro / Luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','delivery','crm','sale','point_of_sale','hr','customer_modifier','product_pack',
                'aikchin_modifier_fields','partner_credit_limit','bi_generic_import','branch','aikchin_modifier_fields_sales',
                'employee_appraisal'
                ],
    # always loaded
    'data': [
        'security/aikchin_access_right.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
        'views/point_of_sale.xml',
        'views/employee_evaluation.xml',
        'views/human_resources.xml',
        'security/access_group.xml',
        'security/access_rights_group.xml',
    ],
    # only loaded in demonstration mode
}