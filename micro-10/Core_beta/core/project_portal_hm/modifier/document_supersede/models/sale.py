# -*- coding: utf-8 -*-

from openerp import models, api, _, fields

class sale_order(models.Model):
    _inherit = 'sale.order'

    version_no  = fields.Integer('Version Number', default=1)
    version_ids = fields.One2many('sale.version', 'sale_id', 'Versions')

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = {} if default is None else default.copy()
        default['version_no'] = 1
        return super(sale_order, self).copy(default=default)

    @api.model
    def _get_tracked_fields(self, updated_fields):
        result = super(sale_order, self)._get_tracked_fields(updated_fields)
        track_fields = ['version_no', 'name']
        for field in track_fields:
            if field not in result:
                field_data = self.fields_get([field])
                result[field] = field_data[field]
        return result
    
class sale_version(models.Model):
    _name = 'sale.version'
    _description = 'Sale Version'
    _order = 'id desc'
    
    @api.one
    @api.depends('line_ids', 'line_ids.quantity', 'line_ids.price_unit')
    def _total(self):
        total = 0
        for line in self.line_ids:
            total += line.quantity * line.price_unit
        self.amount_total = total
        
    sale_id        = fields.Many2one('sale.order', 'Sale Order')
    name           = fields.Char('Number')
    update_user_id = fields.Many2one('res.users', 'Updated By')
    update_date    = fields.Date('Updated On')
    amount_total   = fields.Float('Total', compute=_total)
    line_ids       = fields.One2many('sale.version.line', 'version_id', 'Version Lines')
    
class sale_version_line(models.Model):
    _name = 'sale.version.line'
    _description = 'Sale Version Line'
    
    @api.one
    @api.depends('price_unit', 'quantity')
    def _subtotal(self):
        self.sub_total = self.quantity * self.price_unit
        
    version_id = fields.Many2one('sale.version', 'Version')
    product_id = fields.Many2one('product.product', 'Product')
    name       = fields.Char('Description')
    quantity   = fields.Float('Quantity')
    price_unit = fields.Float('Unit Price')
    sub_total  = fields.Float('Amount', compute=_subtotal)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: