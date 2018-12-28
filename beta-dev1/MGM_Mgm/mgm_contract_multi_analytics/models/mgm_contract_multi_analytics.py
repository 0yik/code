from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    # sale_requisition_id = fields.Many2one('sale.requisition', string='Sale Requisition')
    invoice_id = fields.Many2one('account.invoice', String="Invoice")

class MultiAnalyticsAccounting(models.TransientModel):
    _inherit = 'multi.analytics.accounting'

    sale_requisition_id = fields.Many2one('sale.requisition', string='Sale Requisition')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    invoice_id = fields.Many2one('account.invoice', string="Invoice")


class MgmMultiAssignAnalytics(models.TransientModel):
    _inherit = 'mgm.multi.assign.analytics'

    @api.multi
    def save_multi_analytics_accounting_line(self):
        active_model = self._context.get('active_model')
        if active_model == 'account.invoice' or active_model == 'sale.order' or active_model == 'sale.requisition':
            uniq_records = []

            invoice_analytic_line = self.env['invoice.analytic.line']
            active_id = self._context.get('active_id')
            invoice_analytic_line_records = False

            vals = {}
            if active_model == 'sale.requisition':
                invoice_analytic_line_records = invoice_analytic_line.search([('sale_requisition_id', '=', active_id)])
                if not invoice_analytic_line_records:
                    vals.update({
                        'sale_requisition_id': active_id,
                    })

            if active_model == 'sale.order':
                invoice_analytic_line_records = invoice_analytic_line.search([('sale_order_id', '=', active_id)])
                if not invoice_analytic_line_records:
                    #current_record = self.env['sale.order'].browse(active_id)
                    vals.update({
                        'sale_order_id': active_id,
                        #'sale_requisition_id': current_record.sale_requisition_id.id or False
                    })

            if active_model == "account.invoice":
                invoice_analytic_line_records = invoice_analytic_line.search([('invoice_id', '=', active_id)])
                if not invoice_analytic_line_records:
                    #current_record = self.env['account.invoice'].browse(active_id)
                    vals.update({
                        'invoice_id': active_id,
                        #'sale_order_id': current_record.sale_order_id.id or False,
                        #'sale_requisition_id': current_record.sale_order_id.sale_requisition_id or False
                    })

            if invoice_analytic_line_records:
                invoice_analytic_line_records.unlink()

            for record in self.multi_analytics_accounting_line:
                if record.analytic_account_level_id.id not in uniq_records:
                    uniq_records.append(record.analytic_account_level_id.id)
                    vals.update({
                        'analytic_account_level_id': record.analytic_account_level_id.id or False,
                        'analytic_account_id': record.analytic_account_id.id or False,
                    })
                    invoice_analytic_line.create(vals)
                else:
                    raise UserError(_('The %s is used.') % record.analytic_account_level_id.name)

            return True

    @api.model
    def default_get(self, fields):
        res = super(MgmMultiAssignAnalytics, self).default_get(fields)
        active_model = self._context.get('active_model')

        if active_model == 'account.invoice' or active_model == 'sale.order' or active_model == 'sale.requisition':
            line_vals = []
            current_record_analytic_lines = False

            invoice_analytic_line = self.env['invoice.analytic.line']
            active_id = self._context.get('active_id')

            account_analytic_level_records = self.env["account.analytic.level"].search(
                [('name', 'in', ['Location', 'Business Unit', 'Contract', 'Project', 'Asset', 'Department'])])

            if active_model == 'account.invoice':
                self.name_get()
                current_record = self.env['account.invoice'].browse(active_id)
                current_record_analytic_lines = invoice_analytic_line.search([('invoice_id', '=', active_id)])

                if not current_record_analytic_lines and current_record.sale_order_id:
                    current_record_analytic_lines = invoice_analytic_line.search(
                        [('sale_order_id', '=', current_record.sale_order_id.id)])

                    for current_record_analytic_line in current_record_analytic_lines:
                        invoice_analytic_line.create({
                            'analytic_account_level_id': current_record_analytic_line.analytic_account_level_id.id or False,
                            'analytic_account_id': current_record_analytic_line.analytic_account_id.id or False,
                            'invoice_id':active_id,
                        })


            if active_model == 'sale.order':
                self.name_get()
                current_record = self.env['sale.order'].browse(active_id)
                current_record_analytic_lines = invoice_analytic_line.search([('sale_order_id', '=', active_id)])

                if not current_record_analytic_lines and current_record.requisition_id:
                    current_record_analytic_lines = invoice_analytic_line.search(
                        [('sale_requisition_id', '=', current_record.requisition_id.id)])

                    for current_record_analytic_line in current_record_analytic_lines:
                        invoice_analytic_line.create({
                            'analytic_account_level_id': current_record_analytic_line.analytic_account_level_id.id or False,
                            'analytic_account_id': current_record_analytic_line.analytic_account_id.id or False,
                            'sale_order_id':active_id,
                        })

            if active_model == 'sale.requisition':
                current_record_analytic_lines = invoice_analytic_line.search([('sale_requisition_id', '=', active_id)])

            if current_record_analytic_lines:
                for current_record_analytic_line in current_record_analytic_lines:
                    line_vals.append((0, 0, {'analytic_account_id': current_record_analytic_line.analytic_account_id.id,
                                       'analytic_account_level_id': current_record_analytic_line.analytic_account_id.level_id.id,}))
                    res.update({'multi_analytics_accounting_line':line_vals,})
            else:
                for account_analytic_level_record in account_analytic_level_records:
                    line_vals.append((0, 0, {'analytic_account_level_id': account_analytic_level_record.id,}))
                    res.update({'multi_analytics_accounting_line':line_vals,})

        return res
