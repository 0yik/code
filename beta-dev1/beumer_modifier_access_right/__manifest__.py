# -*- encoding: utf-8 -*-
{
    'name': 'Beumer Modifier Access Right',
    'version': '1.0',
    'category': 'Report',
    'author': 'HashMicro / Quy / Hoang',
    'description': """
        
                """,
    'website': 'www.hashmicro.com',
    'depends': ['base', 'account', 'purchase', 'sale', 'stock', 'hr', 'cost_element',
                'hr_timesheet_sheet', 'product', 'sg_partner_payment','hr_contract','sg_hr_employee',
                'contract_cost_element_budget', 'analytic', 'purchase_request', 'purchase_requisition', 'purchase',
                'hr_expense', 'acc_recurring_entries', 'sg_pettycash', 'sg_partner_payment',
                'sg_hr_holiday', 'multiple_leave_application', 'account_asset', 'hr_holidays', 'team_configuration',
                'multi_category_analytic_account', 'acc_recurring_entries','hr_payroll'
                ],
    'data': [
        'security/access_right_group.xml',
        'security/ir.model.access.csv',
        # 'views/project_team_member.xml',
        'views/hr_holiday_public_view.xml',
        'views/payroll_modifier_fields.xml',
        'views/account_invoice_access_right.xml',
        'views/human_resources_access_right.xml',
        'views/accounting_view.xml',
        # 'views/hr_timesheet_sheet_views.xml',
        'views/account_analytic_analysis_view.xml',
        'views/account_move_view.xml',
        'views/accouting_recurring_view.xml',
        'views/project_cost_element_access_right.xml',
    ],

}
