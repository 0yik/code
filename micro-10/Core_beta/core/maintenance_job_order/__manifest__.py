# -*- coding: utf-8 -*-
{
    'name': "maintenance_job_order",

    'summary': """
         Allow users to create multiple Job Orders to tag to a Maintenance Request """,

    'description': """
        Allow users to create multiple Job Orders to tag to a Maintenance Request.
    """,

    'author': "Hashmicro / Duy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Maintenance',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','maintenance','maintenance_extended', 'hm_facility'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/job_order_view.xml',
    ],
    # only loaded in demonstration mode

}