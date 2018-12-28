# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Invoice(models.Model):
    _inherit = 'account.invoice'



    @api.multi
    @api.depends('permit_no')
    def get_permit_value_diplay(self):
        for rec in self:
            permit_value_diplay = False
            if rec.permit_no:
                permit_value_diplay = True
            rec.permit_value_diplay= permit_value_diplay

    permit_value = fields.Float(string='Permit Value',
       store=True, readonly=False, compute=False)
    permit_value_diplay = fields.Boolean(compute="get_permit_value_diplay", string='Permit Value')

    @api.onchange('invoice_line_ids')
    def onchange_permit_amount(self):
        if self.invoice_line_ids:
            total = 0
            for line in self.invoice_line_ids:
                total = total + line.quantity * line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            self.permit_value = self.currency_id.compute(total, self.env.user.company_id.currency_id)

    @api.multi
    def get_invoice_tax_line_ids(self):
        tax_boj = self.env['account.invoice.tax'].sudo()
        for rec in self:
            old_taxes = tax_boj.search([('invoice_id', '=', rec.id)])
            if old_taxes:
                old_taxes.unlink()
            taxes_grouped = rec.get_taxes_values()
            # tax_lines = rec.tax_line_ids.filtered('manual')
            for tax in taxes_grouped.values():
                tax['invoice_id'] = rec.id
                tax_boj.create(tax)
                # tax_lines += tax_lines.new(tax)

    @api.multi
    def set_tax_in_lines(self):
        tax_obj = self.env['account.tax'].sudo()
        account_tax_final = False
        account_tax = tax_obj.search([('name', 'in', ['Purchase Tax 7% IM'])], limit=1)
        account_tax_other = tax_obj.search([('amount', '=', 7),('amount_type', '=', 'percent')], limit=1)
        if account_tax:
            account_tax_final = account_tax
        elif account_tax_other:
            account_tax_final = account_tax_other
        if account_tax_final:
            for rec in self:
                for one_order_line in rec.invoice_line_ids:
                    one_order_line.invoice_line_tax_ids = account_tax_final

    @api.model
    def tax_line_move_line_get(self):
        res = []
        # keep track of taxes already processed
        done_taxes = []
        # loop the invoice.tax.line in reversal sequence
        account_tax_final = False

        for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
            if tax_line.amount:
                account_tax_final = tax_line
                if tax_line.name == 'Purchase Tax 7% IM':
                    break

        if account_tax_final:
            tax = account_tax_final.tax_id
            if tax.amount_type == "group":
                for child_tax in tax.children_tax_ids:
                    done_taxes.append(child_tax.id)
            res.append({
                'invoice_tax_line_id': account_tax_final.id,
                'tax_line_id': account_tax_final.tax_id.id,
                'type': 'tax',
                'name': account_tax_final.name,
                'price_unit': self.amount_tax,
                'quantity': 1,
                'price': self.amount_tax,
                'account_id': account_tax_final.account_id.id,
                'account_analytic_id': account_tax_final.account_analytic_id.id,
                'invoice_id': self.id,
                'tax_ids': [(6, 0, list(done_taxes))] if account_tax_final.tax_id.include_base_amount else []
            })
            done_taxes.append(tax.id)
        return res

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice',
                 'type','permit_value')
    def _compute_amount(self):
        res = super(Invoice, self)._compute_amount()
        if self.permit_value:
            tax_obj = self.env['account.tax'].sudo()
            account_tax_final = False
            account_tax = tax_obj.search([('name', 'in', ['Purchase Tax 7% IM'])], limit=1)
            for tax in self.tax_line_ids:
                account_tax_final = tax_obj.search([('name', '=', tax.name)], limit=1)
                if tax.name == account_tax.name:
                    break
            if account_tax_final:
                self.amount_tax = account_tax_final._compute_amount(self.env.user.company_id.currency_id.compute(self.permit_value, self.currency_id), 1)
                self.amount_total = self.amount_untaxed + self.amount_tax
    # @api.model
    # def create(self, values):
    #     res = super(Invoice, self).create(values)
    #     # if res.permit_value_diplay and res.state in ['draft', 'open']:
    #     #     res.set_tax_in_lines()
    #     #     res.get_invoice_tax_line_ids()
    #     return res
    #
    # @api.multi
    # def write(self, values):
    #     res = super(Invoice, self).write(values)
    #     # for rec in self:
    #     #     if rec.permit_value_diplay and rec.state in ['draft', 'open']:
    #     #         rec.set_tax_in_lines()
    #     #         rec.get_invoice_tax_line_ids()
    #     return res