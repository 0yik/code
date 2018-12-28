# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class pick_list(models.Model):
    _name = 'pick.list'
    _rec_name = 'picking_id'
    _description = 'Pick List'

    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float('Quantity')
    picking_id = fields.Many2one('stock.picking', string='Delivery Order')
    wave_id = fields.Many2one('stock.picking.wave', string='Picking Wave')

pick_list()

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_confirm(self):
        for record in self:
            pick_list = {}
            if record.move_lines and record.picking_type_id.code == 'outgoing':
                for line in record.move_lines:
                    pick_list['product_id'] = line.product_id.id
                    pick_list['qty'] = line.product_uom_qty
                    pick_list['picking_id'] = record.id
                    pick_list['wave_id'] = record.wave_id and record.wave_id.id
                    self.env['pick.list'].create(pick_list)
        return super(stock_picking, self).action_confirm()

    @api.multi
    def do_transfer(self):
        for record in self:
            pick_list_id = self.env['pick.list'].search([('picking_id','=',record.id)])
            if pick_list_id:
                pick_list_id.unlink()
        return super(stock_picking, self).do_transfer()

stock_picking()