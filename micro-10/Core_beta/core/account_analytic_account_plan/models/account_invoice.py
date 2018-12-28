# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_line_id = fields.Many2one('account.invoice.line', 'Invoice Line Id')
    analytic_distribution_id = fields.Many2one('account.analytic.distribution',
                                               string='Analytic Distribution', )

    @api.multi
    def create_analytic_lines(self):
        res = super(AccountMoveLine, self).create_analytic_lines()
        # for record in self:
        #     if record.analytic_distribution_id and record.analytic_distribution_id.id:
        #         for line in record.analytic_distribution_id.line_ids:
        #             if line.analytic_account_id and line.analytic_account_id.id:
        #                 data = record._prepare_analytic_line_for_distribution(line.analytic_account_id, line.analytic_account_id.tag_ids, line.rate)[0]
        #                 entry = record.env['account.analytic.line'].create(data)


        return res

    # @api.one
    # def _prepare_analytic_line_for_distribution(self, account, tag, rate):
    #     """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
    #         an analytic account. This method is intended to be extended in other modules.
    #     """
    #     amount = (rate/100) * ((self.credit or 0.0) - (self.debit or 0.0))
    #     return {
    #         'name': self.name,
    #         'date': self.date,
    #         'account_id': account.id,
    #         'tag_ids': [(6, 0, tag.ids)],
    #         'unit_amount': self.quantity,
    #         'product_id': self.product_id and self.product_id.id or False,
    #         'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
    #         'amount': self.company_currency_id.with_context(date=self.date or fields.Date.context_today(self)).compute(
    #             amount, account.currency_id) if account.currency_id else amount,
    #         'general_account_id': self.account_id.id,
    #         # 'ref': self.ref,
    #         'move_id': self.id,
    #         'user_id': self.invoice_id.user_id.id or self._uid,
    #         'journal_id' : self.invoice_line_id.invoice_id.journal_id.id and self.invoice_line_id.invoice_id.journal_id.id or self.move_id.journal_id.id
    #     }

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
    def invoice_line_move_line_get(self):
        res = []
        for line in self.invoice_line_ids:
            if line.quantity == 0:
                continue
            tax_ids = []
            for tax in line.invoice_line_tax_ids:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
            # To fix the problem of when subtotal is including tax
            currency = line.invoice_id and line.invoice_id.currency_id or None
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = False
            price_subtotal = line.quantity * price
            # if line.invoice_line_tax_ids:
            #     taxes = line.invoice_line_tax_ids.compute_all(price, currency, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            #     price_subtotal = taxes['total_excluded'] if taxes else line.quantity * price
            flag = False
            for sub_line in line.analytic_distribution_id.line_ids:
                sub_amount = (sub_line.rate/100) * price_subtotal
                move_line_dict = {
                    'invl_id': line.id,
                    'type': 'src',
                    'name': line.name and line.name.split('\n')[0][:64] or '',
                    'price_unit': line.price_unit,
                    'quantity': line.quantity,
                    'price': sub_amount,
                    'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'account_analytic_id': sub_line.analytic_account_id.id,
                    'tax_ids': tax_ids,
                    'invoice_id': self.id,
                    'analytic_tag_ids': analytic_tag_ids,

                    'analytic_distribution_id': line.analytic_distribution_id.id,
                }
                if sub_line['analytic_account_id']:
                    data = {
                        'name': line.name,
                        'date': line.invoice_id.date_invoice,
                        'account_id': sub_line.analytic_account_id.id,
                        'unit_amount': line.quantity,
                        'amount': line.price_subtotal_signed < 0 and -sub_amount or sub_amount,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.uom_id.id,
                        'general_account_id': line.account_id.id,
                        'ref': line.invoice_id.number,
                    }
                    move_line_dict['analytic_line_ids'] = [(0, 0, data)]
                flag = True
            if not flag:
                move_line_dict = {
                    'invl_id': line.id,
                    'type': 'src',
                    'name': line.name.split('\n')[0][:64],
                    'price_unit': line.price_unit,
                    'quantity': line.quantity,
                    'price': line.price_subtotal,
                    'account_id': line.account_id.id,
                    'product_id': line.product_id.id,
                    'uom_id': line.uom_id.id,
                    'account_analytic_id': line.account_analytic_id.id,
                    'tax_ids': tax_ids,
                    'invoice_id': self.id,
                    'analytic_tag_ids': analytic_tag_ids
                }
                if line['account_analytic_id']:
                    move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
                res.append(move_line_dict)
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(account_invoice, self).line_get_convert(line, part)
        if line.get('analytic_distribution_id', False) and line.get('invl_id', False):
            res.update({
                'invoice_line_id' : line.get('invl_id'),
                'analytic_distribution_id': line.get('analytic_distribution_id', False),
            })
        return res

    @api.model
    def default_get(self, fields):
        res = super(account_invoice, self).default_get(fields)

        return res
