# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError


class arkco_modifier_products(models.Model):
    _inherit = 'product.template'

    room_flag = fields.Boolean(string="Is a room?")
    nup_price = fields.Float(string="NUP price")
    booking_price = fields.Float(string="Booking price")
    unit_floor = fields.Float(string="Unit Floor")
    unit_column = fields.Float(string="Unit Room")
    unit_status = fields.Selection([
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rent', 'Rent'),
        ('reserved', 'Reserved'),
        ('no_sale', 'Not for Sale')
        ], string='Status Unit', index=True, copy=False, default='available', track_visibility='onchange')

    @api.onchange('room_flag')
    def change_purchase_ok(self):
        for rec in self:
            if rec.room_flag:
                rec.purchase_ok = False 

    @api.model
    def create(self, vals):
        res = super(arkco_modifier_products, self).create(vals)
        if res.room_flag:
            res.purchase_ok = False
    	return res

    @api.multi
    def write(self, values):
        res = super(arkco_modifier_products, self).write(values)
        if 'room_flag' in values:
            if self.room_flag:
                self.purchase_ok = False
        return res


class CustomProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('room_flag')
    def change_purchase_ok(self):
        for rec in self:
            if rec.room_flag:
                rec.purchase_ok = False 

    @api.model
    def create(self, vals):
        res = super(CustomProductProduct, self).create(vals)
        if res.room_flag:
            res.purchase_ok = False
        return res

    @api.multi
    def write(self, values):
        res = super(CustomProductProduct, self).write(values)
        if 'room_flag' in values:
            if self.room_flag:
                self.purchase_ok = False
        return res

class custom_room_check(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    @api.multi
    def change_product_qty(self):
        warehouse_id = self.env['stock.warehouse'].search([('lot_stock_id','=',self.location_id.id)])
        quant_ids = self.env['stock.quant'].search([('location_id','=',self.location_id.id)])

        if self.product_id.room_flag:
            row = float(warehouse_id.row)
            column = float(warehouse_id.column)
            if (self.product_id.unit_floor<=row) and (self.product_id.unit_column<=column):
                for quant in quant_ids:
                    if (quant.product_id.room_flag) and (quant.product_id != self.product_id):
                        if (float(quant.product_id.unit_floor) == self.product_id.unit_floor) and (float(quant.product_id.unit_column) == self.product_id.unit_column):
                            raise ValidationError(("Product %s already available in room."% quant.product_id.name))
            else:
                raise ValidationError(("Room is not available in the warehouse %s"% warehouse_id.name))
            res = super(custom_room_check,self).change_product_qty()
            return {'type': 'ir.actions.act_window_close'}
        else:
            res = super(custom_room_check,self).change_product_qty()
            return {'type': 'ir.actions.act_window_close'}
