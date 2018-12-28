# -*- coding: utf-8 -*-
{
    'name': "maintenance_invoice",

    'summary': """
         Allow users to enter the invoiceable cost per maintenance request and invoice to customer """,

    'description': """
        Allow users to enter the invoiceable cost per maintenance request and invoice to customer.
    """,

    'author': "Hashmicro / Duy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Maintenance',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','maintenance','maintenance_extended', 'maintenance_job_order','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/job_order_view.xml',
    ],
    # only loaded in demonstration mode

}