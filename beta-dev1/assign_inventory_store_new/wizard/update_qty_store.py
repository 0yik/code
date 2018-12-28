# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from odoo.exceptions import UserError


class UpdateQtyStore(models.TransientModel):
    _name = 'update.qty.store'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Template', required=True)
    product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count')
    new_quantity = fields.Integer('Set Standard Qty Store', default=1,
        required=True, help='')
    new_quantity_on_hand = fields.Integer('New Quantity on Hand', default=1,
        required=True, help='')
    location_id = fields.Many2one(
        'stock.location', 'Store Location',
        required=True, domain="[('usage', '=', 'internal'),('is_shop', '=', True),]")
   # location_id = fields.Many2one(
   #     'stock.warehouse', 'Store Location',
   #     required=True, domain="[('is_shop', '=', True),]")


    @api.model
    def default_get(self, fields):
        res = super(UpdateQtyStore, self).default_get(fields)
        if not res.get('product_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'product.template' and self.env.context.get('active_id'):
            res['product_id'] = self.env['product.product'].search([('product_tmpl_id', '=', self.env.context['active_id'])], limit=1).id
            res['new_quantity'] = self.env['product.product'].search([('product_tmpl_id', '=', self.env.context['active_id'])], limit=1).qty_min_store
            res['new_quantity_on_hand'] = self.env['product.product'].search([('product_tmpl_id', '=', self.env.context['active_id'])], limit=1).qty_new_store
        elif not res.get('product_id') and self.env.context.get('active_id') and self.env.context.get('active_model') == 'product.product' and self.env.context.get('active_id'):
            res['product_id'] = self.env['product.product'].browse(self.env.context['active_id']).id
            res['new_quantity'] = self.env['product.product'].browse(self.env.context['active_id']).qty_min_store
            res['new_quantity_on_hand'] = self.env['product.product'].search([('product_tmpl_id', '=', self.env.context['active_id'])], limit=1).qty_new_store
        # if 'location_id' in fields and not res.get('location_id'):
        #    res['location_id'] = self.env.ref('stock.stock_location_stock').id
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_tmpl_id = self.onchange_product_id_dict(self.product_id.id)['product_tmpl_id']

    def onchange_product_id_dict(self, product_id):
        return {
            'product_tmpl_id': self.env['product.product'].browse(product_id).product_tmpl_id.id,
        }

    @api.model
    def create(self, values):
        if values.get('product_id'):
            values.update(self.onchange_product_id_dict(values['product_id']))
        return super(UpdateQtyStore, self).create(values)

    @api.constrains('new_quantity')
    def check_new_quantity(self):
        if any(wizard.new_quantity < 0 for wizard in self):
            raise UserError(_('Set Standard Qty Store cannot be negative.'))

    @api.constrains('new_quantity_on_hand')
    def check_new_quantity(self):
        if any(wizard.new_quantity_on_hand < 0 for wizard in self):
            raise UserError(_('New Quantity on Hand cannot be negative.'))

    @api.multi
    def change_store_product_qty(self):
        for self_obj in self:
            print "%%%%%%%%%"
            self_obj.product_id.write({'qty_min_store': self_obj.new_quantity,
                                       'qty_new_store': self_obj.new_quantity_on_hand,
                                        })
        return {'type': 'ir.actions.act_window_close'}



UpdateQtyStore()

