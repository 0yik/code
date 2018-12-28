# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class res_assemble(models.Model):
    _inherit = 'res.assemble'

    @api.multi
    def action_assemble(self):
        if not self.material_id:
            raise UserError('Can not assemble without materials')
        for line in self.material_id:
            available_qty = self.compute_product_qty(line.product_id.id)
            if line.qty_pro > available_qty:
                raise UserError(
                    '%s : Quantity greater than the on hand quantity (%s)' % (line.product_id.name, available_qty))
        dest_location = self.env['stock.location'].search([('usage', '=', 'production')], limit=1)
        # Calculating the product_data from the materials
        product_data = {}
        for line in self.material_id:
            self.stock_production_prod.write({'material_ids': [(4, [line.id])]})
            if line.product_id.id not in product_data:
                product_data.update({line.product_id.id: line.qty_pro})
            else:
                product_data.update({line.product_id.id: line.qty_pro + product_data.get(line.product_id.id)})
        if self.stock_production_prod and self.product_id :
            for line in self.material_id:
                self.stock_production_prod.write({'material_ids': [(4, [line.id])]})
            if sum(self.stock_production_prod.quant_ids.mapped('qty')) <= 0:
                for record in self:
                    product_obj = self.env['product.product'].search([('product_tmpl_id', '=', record.product_id.id)], limit=1)
                    # increasing qty of main product
                    vals = {
                        'product_id': product_obj.id,
                        'product_uom_qty': record.quantity_pro,
                        'product_uom': product_obj.uom_id.id,
                        'name': product_obj.name,
                        'date_expected': fields.Datetime.now(),
                        'procure_method': 'make_to_stock',
                        'location_id': dest_location.id,
                        'location_dest_id': record.location_src_id.id,
                        'origin': record.name,
                        'restrict_lot_id': record.stock_production_prod.id or False,
                    }
                    move = self.env['stock.move'].create(vals)
                    move.action_confirm()
                    move.action_done()

                    # decreasing material qty
                    for product_id in product_data:
                        if product_data.get(product_id):
                            lot_line_id = self.env['assemble.materials'].search(
                                [('assemble_id', '=', record.id), ('product_id', '=', product_id)])
                            product_obj = self.env['product.product'].browse(product_id)
                            stock_move = {
                                'product_id': product_obj.id,
                                'product_uom_qty': product_data.get(product_id),
                                'product_uom': product_obj.uom_id.id,
                                'name': product_obj.name,
                                'date_expected': fields.Datetime.now(),
                                'procure_method': 'make_to_stock',
                                'location_id': record.location_src_id.id,
                                'location_dest_id': dest_location.id,
                                'origin': record.name,
                                'restrict_lot_id': lot_line_id.stock_lot.id or False,
                            }
                            move = self.env['stock.move'].create(stock_move)
                            move.action_confirm()
                            move.action_done()
            else:
                for line in self.material_id:
                    # product_obj = self.env['product.product'].browse(product_id)
                    stock_move = {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.qty_pro,
                        'product_uom': line.product_id.uom_id.id,
                        'name': line.product_id.name,
                        'date_expected': fields.Datetime.now(),
                        'procure_method': 'make_to_stock',
                        'location_id': self.location_src_id.id,
                        'location_dest_id': dest_location.id,
                        'origin': self.name,
                        'restrict_lot_id': line.stock_lot.id or False,
                    }
                    move = self.env['stock.move'].create(stock_move)
                    move.action_confirm()
                    move.action_done()
        for line in self.material_id:
            if line.stock_lot and line.stock_lot.is_used == False:
                line.stock_lot.write({'is_used': True})
            elif line.stock_lot.is_used == True:
                raise ValidationError(
                    _('%s Serial Number of %s have been used !' % (line.stock_lot.name, line.product_id.name)))
        self.write({'state': 'done'})
        return True