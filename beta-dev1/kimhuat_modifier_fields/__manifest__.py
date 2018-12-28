# -*- coding: utf-8 -*-
{
    'name': "kimhuat_modifier_fields",

    'summary': """
        """,

    'description': """
        Kimhuat modifier fields
    """,

    'author': "HashMicro / Luc  / Hoang / Sang / Duy",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['calendar','base','product','sale','account', 'stock',
                'purchase_request','purchase_request_to_requisition', 'purchase',
                'hr_holidays','hr','hr_contract',
                'analytic', 'stable_account_analytic_analysis',
                'booking_service_V2', 'booking_service_restriction_reusable',
                'l10n_sg_hr_payroll',
                'purchase_requisition',
                'sg_hr_employee',
                'sg_account_report',
                ],

    # always loaded
    'data': [
    	'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/hide_view.xml',
        'views/booking_order_view.xml',
        'views/work_order_view.xml',
        'views/payment_inherit.xml',
        'wizards/reschdule_booking_view.xml',
        'views/kimhuat_modifier_fields_partner_view.xml',
        'views/kimhuat_modifier_fields_product_view.xml',
        'views/kimhuat_modifier_fields_sales_order_view.xml',
        'views/kimhuat_modifier_fields_purchase_view.xml',
        'views/kimhuat_modifier_fields_invoice_view.xml',
        'views/kimhuat_modifier_fields_employee.xml',
        'views/kimhuat_modifier_fields_calendar.xml',
        'views/account_analytic_account_view.xml',
        'views/kimhuat_modifier_fields_expense.xml',
        'views/kimhuat_booking_view.xml',
        'views/crm_lead_views.xml',
        'views/quotation_views.xml',
        'views/delete_report.xml',
        'views/Sale_view_inherit.xml',
        'views/kimhuat_modifier_date_not_time.xml',
		'views/kimhuat_modifier_fields_stock_picking_view.xml',
		'views/template.xml',
        'views/kimhuat_modifier_fields_hr_employee_view.xml',
        'views/employee_report.xml',
        'views/kimhuat_modifier_fields_hr_employee_view.xml',
        # 'views/calendar_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
