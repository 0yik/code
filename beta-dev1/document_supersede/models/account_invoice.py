# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    version_no  = fields.Integer('Version Number', default=1)
    version_ids = fields.One2many('invoice.version', 'invoice_id', 'Versions')

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = {} if default is None else default.copy()
        default['version_no'] = 1
        return super(account_invoice, self).copy(default=default)

class invoice_version(models.Model):
    _name = 'invoice.version'
    _description = 'Invoice Version'
    _order = 'id desc'
    
    @api.one
    @api.depends('line_ids', 'line_ids.quantity', 'line_ids.price_unit')
    def _total(self):
        total = 0
        for line in self.line_ids:
            total += line.quantity * line.price_unit
        self.amount_total = total
        
    invoice_id     = fields.Many2one('account.invoice', 'Invoice')
    name           = fields.Char('Number')
    update_user_id = fields.Many2one('res.users', 'Updated By')
    update_date    = fields.Date('Updated On')
    amount_total   = fields.Float('Total', compute=_total)
    line_ids       = fields.One2many('invoice.version.line', 'version_id', 'Version Lines')
    
class invoice_version_line(models.Model):
    _name = 'invoice.version.line'
    _description = 'Invoice Version Line'
    
    @api.one
    @api.depends('price_unit', 'quantity')
    def _subtotal(self):
        self.sub_total = self.quantity * self.price_unit
        
    version_id = fields.Many2one('invoice.version', 'Version')
    product_id = fields.Many2one('product.product', 'Product')
    name       = fields.Char('Description')
    quantity   = fields.Float('Quantity')
    price_unit = fields.Float('Unit Price')
    sub_total  = fields.Float('Amount', compute=_subtotal)
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: