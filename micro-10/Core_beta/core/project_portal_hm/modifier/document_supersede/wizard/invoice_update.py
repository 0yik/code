# -*- coding: utf-8 -*-
import time
from odoo import models, api, _, fields

class invoice_update(models.TransientModel):
    _name = 'invoice.update'
    _description = 'Invoice Update'

    def _get_invoice(self):
        return self._context['active_id']

    def _get_invoice_lines(self):
        invoice_lines = []
        invoice = self.env['account.invoice'].browse(self._context['active_id'])
        for line in invoice.invoice_line_ids:
            invoice_lines.append({
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'sub_total': line.quantity * line.price_unit,
                'invoice_line_id': line.id
            })
        return invoice_lines

    @api.one
    @api.depends('invoice_lines', 'invoice_lines.quantity', 'invoice_lines.price_unit')
    def _total(self):
        total = 0
        for line in self.invoice_lines:
            total += line.quantity * line.price_unit
        self.amount_total = total

    invoice_id    = fields.Many2one('account.invoice', 'Invoice', default=_get_invoice, ondelete='cascade', index=True)
    invoice_lines = fields.One2many('invoice.update.line', 'invoice_id', 'Lines', default=_get_invoice_lines, ondelete='cascade', index=True)
    amount_total  = fields.Float('Total Amount', compute=_total)

    @api.one
    def action_update(self):
        invoice = self.invoice_id
        version = self.env['invoice.version'].create({
            'name': invoice.number,
            'update_user_id': self.env.user.id,
            'update_date': time.strftime('%Y-%m-%d'),
            'invoice_id': invoice.id
        })
        for line in invoice.invoice_line_ids:
            self.env['invoice.version.line'].create({
                'version_id': version.id,
                'product_id': line.product_id and line.product_id.id or False ,
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit
            })
        rem_invlines = self.invoice_lines.mapped('invoice_line_id')
        lines_todelete = invoice.invoice_line_ids - rem_invlines
        lines_todelete.unlink()
        for line in self.invoice_lines:
            if line.invoice_line_id:
                line.invoice_line_id.write({
                    'product_id': line.product_id and line.product_id.id or False ,
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit
                })
            else:
                self.env['account.invoice.line'].create({
                    'invoice_id': invoice.id,
                    'product_id': line.product_id and line.product_id.id or False ,
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit
                })
        if invoice.state == 'proforma2' or invoice.state == 'proforma':
            invoice.state = 'proforma2'
        else:
            invoice.action_cancel()
            invoice.action_invoice_draft()
            new_version = invoice.version_no + 1
            invoice.version_no = new_version
            invoice.action_invoice_open()
            invoice.number = invoice.move_name + '(' + str(new_version) + ')'
        return {'type': 'ir.actions.act_window_close'}


class invoice_update_line(models.TransientModel):
    _name = 'invoice.update.line'
    _description = 'Invoice Update Lines'

    @api.one
    @api.depends('price_unit', 'quantity')
    def _subtotal(self):
        self.sub_total = self.quantity * self.price_unit

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.name = self.product_id.name

    invoice_id      = fields.Many2one('invoice.update', 'Invoice',ondelete='cascade', index=True)
    invoice_line_id = fields.Many2one('account.invoice.line', 'Invoice Line',ondelete='cascade', index=True)
    product_id      = fields.Many2one('product.product', 'Product')
    name            = fields.Char('Description')
    quantity        = fields.Float('Quantity')
    price_unit      = fields.Float('Unit Price')
    sub_total       = fields.Float('Amount', compute=_subtotal)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: