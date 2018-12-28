from odoo import fields, models,api
from odoo.exceptions import ValidationError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        if line.analytic_distribution_id:
            res['analytic_distribution_id'] = line.analytic_distribution_id
        return res

    @api.depends('state')
    def _get_entries(self):
        for invoice in self:
            analytic_entry = self.env['account.analytic.line'].search([('invoice_id', '=', invoice.id)])
            print 'Analytic Entry   :   ',   analytic_entry
            invoice.update({
                'analytic_entries_count': len(set(analytic_entry)),
            })

    @api.multi
    def action_view_analytic_entries(self):
        action = self.env.ref('analytic.account_analytic_line_action_entries').read()[0]

        analytic_entries = self.env['account.analytic.line'].search([('invoice_id', '=', self.id)])
        print 'Analytic Entries     :   ',  analytic_entries
        if len(analytic_entries) > 1:
            action['domain'] = [('id', 'in', analytic_entries.ids)]
        elif analytic_entries:
            action['views'] = [(self.env.ref('analytic.view_account_analytic_line_form').id, 'form')]
            action['res_id'] = analytic_entries.id
        return action

    analytic_entries_count = fields.Integer(string='# of Analytic Entries', compute='_get_entries', readonly=True)

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        for line in self.invoice_line_ids:
            if line.quantity == 0:
                continue
            # To fix the problem of when subtotal is including tax
            currency = line.invoice_id and line.invoice_id.currency_id or None
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_subtotal = line.quantity * price
            flag = False
            analytic_distribution_ids = []
            for sub_line in line.analytic_distribution_id:
                sub_amount = (sub_line.rate / 100) * price_subtotal
                data = {
                    'name': line.name,
                    'partner_id': line.partner_id.id,
                    'invoice_id': line.invoice_id.id,
                    'date': line.invoice_id.date_invoice,
                    'account_id': sub_line.analytic_account_id.id,
                    'analytic_level_id': sub_line.analytic_level_id.id,
                    'unit_amount': line.quantity,
                    'amount': line.invoice_id.type in ['in_invoice', 'out_refund'] and -sub_amount or sub_amount,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.uom_id.id,
                    'general_account_id': line.account_id.id,
                    'ref': line.invoice_id.number,
                }
                journal_entry_id = self.env['account.analytic.line'].create(data)
        return res

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']

        res = super(AccountInvoiceLine, self).default_get(fields)
        res['check_analytic_account'] = self.user_has_groups('analytic.group_analytic_accounting')
        return res

    def _check_distribution_account(self):
        IrConfigParam = self.env['ir.config_parameter']
        for line in self:
            line.check_distribution_sale = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_sale')
            line.check_analytic_account_sale = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_account_for_sales')
            line.check_distribution_purchase = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_purchases')
            line.check_analytic_account_purchase = self.user_has_groups('purchase.group_analytic_accounting')
            line.check_analytic_account = self.user_has_groups('analytic.group_analytic_accounting')
            print 'Analytic Account Check   :   ', line.check_analytic_account


    check_distribution_sale = fields.Boolean(compute="_check_distribution_account", string='Distribution Check Sales')
    check_analytic_account_sale = fields.Boolean(compute="_check_distribution_account", string='Analytic Account Check Sales')
    check_distribution_purchase = fields.Boolean(compute="_check_distribution_account", string='Distribution Check Purchase')
    check_analytic_account_purchase = fields.Boolean(compute="_check_distribution_account", string='Analytic Account Check Purchase')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account", string='Analytic Account Check')
    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'invoice_line_id', string='Analytic Distribution')

    def check_lines(self, res):
        for line_item in res.analytic_distribution_id:
            if line_item.rate:
                line_rate = res.analytic_distribution_id.search([('invoice_line_id', '=', res.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
                amount = [a.rate for a in line_rate ]
                if sum(amount) != 100:
                    raise ValidationError(
                        ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

    @api.model
    def create(self, values):
        line = super(AccountInvoiceLine, self).create(values)
        self.check_lines(line)
        return line

    @api.multi
    def write(self, values):
        result = super(AccountInvoiceLine, self).write(values)
        self.check_lines(self)
        return result