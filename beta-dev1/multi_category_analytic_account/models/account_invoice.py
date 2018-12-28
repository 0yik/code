# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_line_id = fields.Many2one('account.invoice.line', 'Invoice Line Id')
    analytic_distribution_id = fields.Many2one('account.analytic.distribution', related='invoice_line_id.analytic_distribution_id', string='Analytic Distribution')

    @api.multi
    def create_analytic_lines(self):
        res = super(AccountMoveLine, self).create_analytic_lines()
        for record in self:
            if record.analytic_distribution_id and record.analytic_distribution_id.id:
                for line in record.analytic_distribution_id.line_ids:
                    if line.analytic_account_id and line.analytic_account_id.id:
                        data = record._prepare_analytic_line_for_distribution(line.analytic_account_id, line.analytic_account_id.tag_ids, line.rate)[0]
                        entry = record.env['account.analytic.line'].create(data)
                        entry.write({
                            'general_account_id': record.invoice_line_id.invoice_id.account_id.id
                        })

        return res

    @api.one
    def _prepare_analytic_line_for_distribution(self, account, tag, rate):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            an analytic account. This method is intended to be extended in other modules.
        """
        amount = (rate/100) * ((self.credit or 0.0) - (self.debit or 0.0))
        return {
            'name': self.name,
            'date': self.date,
            'account_id': account.id,
            'tag_ids': [(6, 0, tag.ids)],
            'unit_amount': self.quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
            'amount': self.company_currency_id.with_context(date=self.date or fields.Date.context_today(self)).compute(
                amount, account.currency_id) if account.currency_id else amount,
            'general_account_id': self.invoice_line_id.invoice_id.account_id.id,
            'ref': self.ref,
            'move_id': self.id,
            'user_id': self.invoice_id.user_id.id or self._uid,
            'journal_id' : self.invoice_line_id.invoice_id.journal_id.id
        }

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    analytic_distribution_id = fields.Many2one('account.analytic.distribution', string='Analytic Distribution')

    @api.multi
    def create_analytic(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.distribution',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id'   : self.analytic_distribution_id.id,
            'target': 'new',
            'context': self.id
        }

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(account_invoice, self)._prepare_invoice_line_from_po_line(line)
        if line.analytic_distribution_id and line.analytic_distribution_id.id:
            res['analytic_distribution_id'] = line.analytic_distribution_id.id
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(account_invoice, self).line_get_convert(line, part)
        if line.get('invl_id', False):
            res.update({
                'invoice_line_id' : line.get('invl_id')
            })
        return res

    @api.model
    def default_get(self, fields):
        res = super(account_invoice, self).default_get(fields)

        return res
