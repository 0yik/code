# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Invoice(models.Model):
    _inherit = 'account.invoice'

    included_tax = fields.Boolean("Is included tax ?")

    @api.multi
    def action_invoice_open(self):
        res = super(Invoice, self).action_invoice_open()
        for rec in self:
            if rec.included_tax:
                rec.number += '01'
            else:
                rec.number += '02'
        return res


class sale_order(models.Model):
    _inherit = 'sale.order'

    # @api.multi
    # def action_confirm(self):
    #     res = super(sale_order, self).action_confirm()
    #     if res:
    #         self.action_invoice_create(final=True)
    #     return res

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(sale_order, self).action_invoice_create(grouped, final)
        list_id = []
        for id in res:
            tax_flag = False
            untax_flag = False
            origin_inv = self.env['account.invoice'].browse(id)
            list_id.append(origin_inv.id)
            for line in origin_inv.invoice_line_ids:
                if line.invoice_line_tax_ids:
                    tax_flag = True
                if not line.invoice_line_tax_ids:
                    untax_flag = True

            if tax_flag == True and untax_flag:
                tax_invoice = origin_inv
                untax_invoice = origin_inv.copy()
                for line in tax_invoice.invoice_line_ids:
                    if not line.invoice_line_tax_ids:
                        line.unlink()
                for line in untax_invoice.invoice_line_ids:
                    if line.invoice_line_tax_ids:
                        line.unlink()
                tax_invoice.included_tax = True
                tax_invoice.compute_taxes()
                untax_invoice.included_tax = False
                untax_invoice.compute_taxes()
                list_id.append(untax_invoice.id)
                return list_id
            else:
                if origin_inv.tax_line_ids:
                    origin_inv.included_tax = True
                else:
                    origin_inv.included_tax = False
        return res