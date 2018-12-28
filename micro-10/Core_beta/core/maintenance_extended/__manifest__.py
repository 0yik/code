# -*- coding: utf-8 -*-
{
    'name': "maintenance_extended",

    'summary': """
         Enhance the functions of maintenance module """,

    'description': """
        Enhance the functions of maintenance module such as setup team members for maintenance team, generate pivot and graph analysis based on maintenance request.
    """,

    'author': "Teksys Enterprises Pvt. Ltd. / Rajnish /Duy",
    'website': "http://www.teksys.in",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Maintenance',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','maintenance','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}