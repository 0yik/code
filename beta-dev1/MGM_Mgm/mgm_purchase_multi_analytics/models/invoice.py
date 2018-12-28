from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    vendor_bill_id = fields.Many2one('account.invoice', String="Invoice")


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_analytic_line_id = fields.One2many('purchase.analytic.line', 'vendor_bill_id', string="Invoice Analytic Lines")
    purchase_order_id = fields.Many2one("purchase.order", "Purchase Order")

    @api.multi
    def multi_analytic_account(self):
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('mgm_multi_assign_analytics', 'mgm_multi_assign_analytics_form')[1]
        except ValueError:
            compose_form_id = False

        res = {
            'type': 'ir.actions.act_window',
            'name': 'Analytics Accounting',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mgm.multi.assign.analytics',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {}
        }
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        for rec in self:

            if rec.number and rec.number != "/":
                current_record_analytic_lines = self.env["account.analytic.line"].search(
                    [('vendor_bill_id', '=', rec.id)])

                if not current_record_analytic_lines:
                    uniq_records = []
                    account_analytic_line = self.env['account.analytic.line']

                    for record in rec.invoice_analytic_line_id:
                        if record.analytic_account_level_id.id not in uniq_records:
                            uniq_records.append(record.analytic_account_level_id.id)
                            account_analytic_line.create({
                                'name': str(record.analytic_account_level_id.name) + " - " + str(rec.number),
                                'account_id': record.analytic_account_id.id or False,
                                'amount': rec.amount_total,
                                'vendor_bill_id': rec.id,
                                'company_id': rec.company_id.id
                            })

        return res