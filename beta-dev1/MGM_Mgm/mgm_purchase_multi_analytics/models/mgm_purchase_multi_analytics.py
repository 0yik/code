from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class InvoiceAnalyticLine(models.Model):
    _name = 'purchase.analytic.line'

    analytic_account_level_id = fields.Many2one('account.analytic.level', string='Analytic Account Level')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    purchase_requisition_id = fields.Many2one('purchase.requisition', string='Purchase Requisition')
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    vendor_bill_id = fields.Many2one('account.invoice', string="Invoice")


class MgmMultiAssignAnalytics(models.TransientModel):
    _inherit = 'mgm.multi.assign.analytics'

    @api.multi
    def save_multi_analytics_accounting_line(self):
        super(MgmMultiAssignAnalytics, self).save_multi_analytics_accounting_line()
        active_model = self._context.get('active_model')
        if active_model == 'account.invoice' or active_model == 'purchase.order' or active_model == 'purchase.requisition':
            uniq_records = []
            vals = {}
            invoice_analytic_line = self.env['purchase.analytic.line']
            active_id = self._context.get('active_id')
            invoice_analytic_line_records = False


            if active_model == 'purchase.requisition':
                invoice_analytic_line_records = invoice_analytic_line.search([('purchase_requisition_id', '=', active_id)])
                if not invoice_analytic_line_records:
                    vals.update({
                        'purchase_requisition_id': active_id,
                    })

            if active_model == 'purchase.order':
                invoice_analytic_line_records = invoice_analytic_line.search([('purchase_order_id', '=', active_id)])
                if not invoice_analytic_line_records:
                    vals.update({
                        'purchase_order_id': active_id,
                    })

            if active_model == "account.invoice":
                invoice_analytic_line_records = invoice_analytic_line.search([('vendor_bill_id', '=', active_id)])
                if not invoice_analytic_line_records:
                    vals.update({
                        'vendor_bill_id': active_id,
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

        if active_model == 'account.invoice' or active_model == 'purchase.order' or active_model == 'purchase.requisition':
            line_vals = []
            current_record_analytic_lines = False

            invoice_analytic_line = self.env['purchase.analytic.line']
            active_id = self._context.get('active_id')

            account_analytic_level_records = self.env["account.analytic.level"].search(
                [('name', 'in', ['Location', 'Business Unit', 'Contract', 'Project', 'Asset', 'Department'])])

            if active_model == 'account.invoice':
                self.name_get()
                current_record = self.env['account.invoice'].browse(active_id)
                current_record_analytic_lines = invoice_analytic_line.search([('vendor_bill_id', '=', active_id)])

                if not current_record_analytic_lines and current_record.purchase_order_id:
                    current_record_analytic_lines = invoice_analytic_line.search(
                        [('purchase_order_id', '=', current_record.purchase_order_id.id)])

                    for current_record_analytic_line in current_record_analytic_lines:
                        invoice_analytic_line.create({
                            'analytic_account_level_id': current_record_analytic_line.analytic_account_level_id.id or False,
                            'analytic_account_id': current_record_analytic_line.analytic_account_id.id or False,
                            'vendor_bill_id':active_id,
                        })


            if active_model == 'purchase.order':
                self.name_get()
                current_record = self.env['purchase.order'].browse(active_id)
                current_record_analytic_lines = invoice_analytic_line.search([('purchase_order_id', '=', active_id)])

                if not current_record_analytic_lines and current_record.requisition_id:
                    current_record_analytic_lines = invoice_analytic_line.search(
                        [('purchase_requisition_id', '=', current_record.requisition_id.id)])

                    for current_record_analytic_line in current_record_analytic_lines:
                        invoice_analytic_line.create({
                            'analytic_account_level_id': current_record_analytic_line.analytic_account_level_id.id or False,
                            'analytic_account_id': current_record_analytic_line.analytic_account_id.id or False,
                            'purchase_order_id':active_id,
                        })


            if active_model == 'purchase.requisition':
                current_record_analytic_lines = invoice_analytic_line.search([('purchase_requisition_id', '=', active_id)])


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

