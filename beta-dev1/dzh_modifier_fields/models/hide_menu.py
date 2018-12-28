from odoo import fields, models, api
from xlrd import open_workbook
import os


class hide_menu(models.TransientModel):
    _name = 'hide.menu'

    @api.model
    def hide_menu(self):

        # crm_lead = self.env['crm.lead'].search([])
        # for lead in crm_lead:
        #     if lead.partner_id:
        #         vals = lead._onchange_partner_id_values(lead.partner_id.id)
        #         lead.write(vals)
        #
        # invoice_line_ids = self.env['account.invoice.line'].search([])
        # for invoice_line_id in invoice_line_ids:
        #     if invoice_line_id.account_user_id:
        #         invoice_line_id.number_user_id = len(invoice_line_id.account_user_id)
        #
        #  Import User ID
        # file = os.path.abspath(__file__).split('models')[0]+'views/import_file_invoice_2-1.xls'
        # workbook = open_workbook(file)
        # sheet = workbook.sheet_by_index(0)
        # thb_currency_id = self.env['res.currency'].search([('name', '=', 'THB')], limit=1).id
        # for row_no in range(sheet.nrows):
        #     val = {}
        #     if row_no <= 0:
        #         fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
        #     else:
        #         line = (map(lambda row: isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value),
        #                     sheet.row(row_no)))
        #         if line:
        #
        #             invoice_id = self.env['account.invoice'].search([('name','=',line[3])],limit=1)
        #             invoice_id.write({
        #                 'currency_id' : thb_currency_id
        #             })
                    # if invoice_id.partner_id and invoice_id.partner_id.partner_users and len(invoice_id.partner_id.partner_users) == 1:
                    #     user_ids = invoice_id.partner_id.partner_users
                    #     for invoice_line in invoice_id.invoice_line_ids:
                    #         invoice_line.write({
                    #             'account_user_id' :  [( 6, 0, [user_ids.id])],
                    #             'number_user_id' : 1
                    #         })
                    # if invoice_id.partner_id and invoice_id.partner_id.partner_users and len(invoice_id.partner_id.partner_users) > 1:
                    #     user_ids = invoice_id.partner_id.partner_users
                    #     for user in user_ids:
                    #         if user.name == line[4]:
                    #             for invoice_line in invoice_id.invoice_line_ids:
                    #                 invoice_line.write({
                    #                     'account_user_id': [(6, 0, [user.id])],
                    #                     'number_user_id': 1
                    #                 })

        # file = os.path.abspath(__file__).split('models')[0] + 'views/import_file_invoice.xls'
        # workbook = open_workbook(file)
        # sheet = workbook.sheet_by_index(0)
        # thb_currency_id = self.env['res.currency'].search([('name', '=', 'MYR')], limit=1).id
        # for row_no in range(sheet.nrows):
        #     val = {}
        #     if row_no <= 0:
        #         fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
        #     else:
        #         line = (map(lambda row: isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value),
        #                     sheet.row(row_no)))
        #         if line:
        #
        #             invoice_id = self.env['account.invoice'].search([('name', '=', line[3])], limit=1)
        #             invoice_id.write({
        #                 'currency_id': thb_currency_id
        #             })
                    # if invoice_id.partner_id and invoice_id.partner_id.partner_users and len(
                    #         invoice_id.partner_id.partner_users) == 1:
                    #     user_ids = invoice_id.partner_id.partner_users
                    #     for invoice_line in invoice_id.invoice_line_ids:
                    #         invoice_line.write({
                    #             'account_user_id': [(6, 0, [user_ids.id])],
                    #             'number_user_id': 1
                    #         })
                    # if invoice_id.partner_id and invoice_id.partner_id.partner_users and len(invoice_id.partner_id.partner_users) > 1:
                    #     user_ids = invoice_id.partner_id.partner_users
                    #     for user in user_ids:
                    #         if user.name == line[4]:
                    #             for invoice_line in invoice_id.invoice_line_ids:
                    #                 invoice_line.write({
                    #                     'account_user_id': [(6, 0, [user.id])],
                    #                     'number_user_id': 1
                    #                 })

        menu_obj = self.env['ir.ui.menu']

        sales_menu = menu_obj.search([('name','=','Sales'),('parent_id','=',None)])
        invoicing_menu = menu_obj.search([('name','=','Invoicing')])
        accounting_menu = menu_obj.search([('name','=','Accounting'),('parent_id','=',None)])


        #Hide Accounting - Report _ pdfreport
        accounting_report = menu_obj.search([('name','=','Reports'),('parent_id','=',accounting_menu.id)])
        accounting_report_pdfreport = menu_obj.search([('name','=','PDF Reports'),('parent_id','=',accounting_report.id)])
        for accounting_report_pdf in accounting_report_pdfreport:
            accounting_report_pdf.write({
                'active' : False
            })

        #Hide Accounting - Sales
        accounting_sales = menu_obj.search([('name', '=', 'Sales'), ('parent_id', '=', accounting_menu.id)])
        for accounting_sale in accounting_sales:
            accounting_sale.write({
                'active' : False
            })

        #Hide Accounting - Purchases
        accounting_purchases = menu_obj.search([('name', '=', 'Purchases'), ('parent_id', '=', accounting_menu.id)])
        for accounting_purchase in accounting_purchases:
            accounting_purchase.write({
                'active': False
            })

        #Hide Accounting - Adviser
        accounting_adviser = menu_obj.search([('name', '=', 'Adviser'), ('parent_id', '=', accounting_menu.id)])
        for accounting_advise in accounting_adviser:
            accounting_advise.write({
                'active': False
            })
        #Menu Accounting - Configuration
        accounting_configuration = menu_obj.search([('name', '=', 'Configuration'), ('parent_id', '=', accounting_menu.id)])

        #Menu Accounting - Configuration - Accounting
        accounting_configuration_acc = menu_obj.search(
            [('name', '=', 'Accounting'), ('parent_id', '=', accounting_configuration.id)])

        #Hide Menu in Accounting - Configuration - Accounting
        accounting_configuration_fiscal_positions = menu_obj.search(
            [('name', '=', 'Fiscal Positions'), ('parent_id', '=', accounting_configuration_acc.id)])
        for accounting_configuration_fiscal_position in accounting_configuration_fiscal_positions:
            accounting_configuration_fiscal_position.write({
                'active': False
            })

        accounting_configuration_bank_accounts = menu_obj.search(
            [('name', '=', 'Bank Accounts'), ('parent_id', '=', accounting_configuration_acc.id)])
        for accounting_configuration_bank_account in accounting_configuration_bank_accounts:
            accounting_configuration_bank_account.write({
                'active': False
            })

        accounting_configuration_journals = menu_obj.search(
            [('name', '=', 'Journals'), ('parent_id', '=', accounting_configuration_acc.id)])
        for accounting_configuration_journal in accounting_configuration_journals:
            accounting_configuration_journal.write({
                'active': False
            })

        accounting_configuration_accounts_tags = menu_obj.search(
            [('name', '=', 'Accounts Tags'), ('parent_id', '=', accounting_configuration_acc.id)])
        for accounting_configuration_accounts_tag in accounting_configuration_accounts_tags:
            accounting_configuration_accounts_tag.write({
                'active': False
            })
        #Hide Accounting - Configuration - Financial Reports
        accounting_configuration_financial_reports = menu_obj.search(
            [('name', '=', 'Financial Reports'), ('parent_id', '=', accounting_configuration.id)])
        for accounting_configuration_financial_report in accounting_configuration_financial_reports:
            accounting_configuration_financial_report.write({
                'active': False
            })

        #Hide Accounting - Configuration - Payments
        accounting_configuration_payments = menu_obj.search(
            [('name', '=', 'Payments'), ('parent_id', '=', accounting_configuration.id)])
        for accounting_configuration_payment in accounting_configuration_payments:
            accounting_configuration_payment.write({
                'active': False
            })

        #Hide Invoicing menu
        for invoicing in invoicing_menu:
            invoicing.write({
                'active' : False
            })

        leads_menu = menu_obj.search([('name','=','Leads')])
        for leads in leads_menu:
            leads.write({
                'active' : False
            })

        quotations_menu = menu_obj.search([('name', '=', 'Quotations')])
        for quotations in quotations_menu:
            quotations.write({
                'active': False
            })

        sales_order_menu = menu_obj.search([('name', '=', 'Sales Orders')])
        for sales_order in sales_order_menu:
            sales_order.write({
                'active': False
            })

        reports_menu = menu_obj.search([('name','=','Reports'),('parent_id','=',sales_menu.id)])
        reports_sales_menu = menu_obj.search([('name', '=', 'Sales'),('parent_id','=',reports_menu.id)])
        for reports_sales in reports_sales_menu:
            reports_sales.write({
                'active': False
            })

        reports_sales_pipeline_menu = menu_obj.search([('name', '=', 'Sales Pipeline'),('parent_id', '=', reports_menu.id)])
        for reports_sales_pipeline in reports_sales_pipeline_menu:
            reports_sales_pipeline.write({
                'active': False
            })

        reports_customer_refund_menu = menu_obj.search([('name', '=', 'Customer Refund'),('parent_id', '=', reports_menu.id)])
        for reports_customer_refund in reports_customer_refund_menu:
            reports_customer_refund.write({
                'active': False
            })

        reports_sales_pipeline_report_menu = menu_obj.search([('name', '=', 'Sales Pipeline Report'),('parent_id', '=', reports_menu.id)])
        for reports_sales_pipeline_report in reports_sales_pipeline_report_menu:
            reports_sales_pipeline_report.write({
                'active': False
            })

        reports_sales_revenue_report_menu = menu_obj.search([('name', '=', 'Sales Revenue Report'),('parent_id', '=', reports_menu.id)])
        for reports_sales_revenue_report in reports_sales_revenue_report_menu:
            reports_sales_revenue_report.write({
                'active': False
            })

        reports_PaLR_menu = menu_obj.search([('name', '=', 'Profit and Loss Report'),('parent_id', '=', reports_menu.id)])
        for reports_PaLR in reports_PaLR_menu:
            reports_PaLR.write({
                'active': False
            })

        pricelists_menu = menu_obj.search([('name','=','Pricelists')])
        for pricelists in pricelists_menu:
            pricelists.write({
                'active': False
            })

