# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.template'

    product_type = fields.Selection([('smartphone', 'Smartphone'), ('accessories', 'Accessories'), ('kartu_perdana', 'Kartu Perdana'), ('pulsa', 'Pulsa')], string='Product Type',default='smartphone')
    pulsa_component_lines = fields.One2many('pulsa.component.line', 'product_tmpl_parent_id',string='component lines')
    smphone_full_name = fields.Char('Full Name')
    smphone_description = fields.Text('Description')

    @api.onchange('pulsa_component_lines')
    def onchange_pulsa_component_lines(self):
        for product in self:
            if product.pulsa_component_lines:
                product.sale_ok = False
                product.purchase_ok = True


class pos_order(models.Model):
    _inherit = 'pos.order'

    def create_picking(self):
        res = super(pos_order,self).create_picking()
        return res

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        if self.env['sale.order'].search([('name','=',self.origin)]):
            picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'internal')],
                limit=1)
            picking_vals_rev_to_inventory = {
                'name': picking_type_id.sequence_id.next_by_id(),
                'picking_type_id': picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.env.ref('stock.location_inventory').id,
                'origin': self.name,
                'state': 'draft',
            }
            picking_vals_rev_to_stock = {
                'name': picking_type_id.sequence_id.next_by_id(),
                'picking_type_id': picking_type_id.id,
                'location_id': self.env.ref('stock.location_inventory').id,
                'location_dest_id': self.location_id.id,
                'origin': self.name,
                'state': 'draft',
            }
            picking_to_inventory_id = False
            picking_to_stock_id = False
            for move in self.move_lines:
                pulsa_component_line = self.env['pulsa.component.line'].search([('product_template_id', '=', move.product_id.product_tmpl_id.id)])
                if pulsa_component_line:
                    # inventory
                    if not picking_to_inventory_id:
                        picking_to_inventory_id = self.env['stock.picking'].create(picking_vals_rev_to_inventory)
                    product = self.env['product.product'].search([('product_tmpl_id','=',pulsa_component_line.product_tmpl_parent_id.id)],limit=1)
                    quantity = move.product_uom._compute_quantity(move.product_uom_qty,pulsa_component_line.product_tmpl_parent_id.uom_id)
                    self.env['stock.move'].create({
                        'product_id': product.id,
                        'name': product.name,
                        'product_uom_qty': quantity,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.env.ref('stock.location_inventory').id,
                        'product_uom': pulsa_component_line.product_tmpl_parent_id.uom_id.id,
                        'origin': self.name,
                        'picking_id': picking_to_inventory_id.id
                    })
                    # stock
                    if not picking_to_stock_id:
                        picking_to_stock_id = self.env['stock.picking'].create(picking_vals_rev_to_stock)
                    product_to_stock = move.product_id
                    quantity_to_stock = move.product_uom._compute_quantity(move.product_uom_qty,product_to_stock.uom_id)
                    self.env['stock.move'].create({
                        'product_id': product_to_stock.id,
                        'name': product_to_stock.name,
                        'product_uom_qty': quantity_to_stock,
                        'location_id': self.env.ref('stock.location_inventory').id,
                        'location_dest_id': self.location_id.id,
                        'product_uom': product_to_stock.uom_id.id,
                        'origin': self.name,
                        'picking_id': picking_to_stock_id.id
                    })
            if picking_to_inventory_id and picking_to_inventory_id.move_lines:
                picking_to_inventory_id.action_confirm()
                picking_to_inventory_id.force_assign()
                picking_to_inventory_id.do_new_transfer()
                stock_transfer_id = self.env['stock.immediate.transfer'].search([('pick_id', '=', picking_to_inventory_id.id)],limit=1)
                stock_transfer_id.process()
                if picking_to_stock_id and picking_to_stock_id.move_lines:
                    picking_to_stock_id.action_confirm()
                    picking_to_stock_id.force_assign()
                    picking_to_stock_id.do_new_transfer()
                    stock_transfer_id = self.env['stock.immediate.transfer'].search(
                        [('pick_id', '=', picking_to_stock_id.id)], limit=1)
                    stock_transfer_id.process()

        return super(stock_picking,self).do_transfer()
    @api.multi
    def action_done(self):
        if self.env['pos.order'].search([('name','=',self.origin)]):
            picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'internal')],
                limit=1)
            picking_vals_rev_to_inventory = {
                'name': picking_type_id.sequence_id.next_by_id(),
                'picking_type_id': picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.env.ref('stock.location_inventory').id,
                'origin': self.name,
                'state': 'draft',
            }
            picking_vals_rev_to_stock = {
                'name': picking_type_id.sequence_id.next_by_id(),
                'picking_type_id': picking_type_id.id,
                'location_id': self.env.ref('stock.location_inventory').id,
                'location_dest_id': self.location_id.id,
                'origin': self.name,
                'state': 'draft',
            }
            picking_to_inventory_id = False
            picking_to_stock_id = False
            for move in self.move_lines:
                pulsa_component_line = self.env['pulsa.component.line'].search([('product_template_id', '=', move.product_id.product_tmpl_id.id)])
                if pulsa_component_line:
                    # inventory
                    if not picking_to_inventory_id:
                        picking_to_inventory_id = self.env['stock.picking'].create(picking_vals_rev_to_inventory)
                    product = self.env['product.product'].search([('product_tmpl_id','=',pulsa_component_line.product_tmpl_parent_id.id)],limit=1)
                    quantity = move.product_uom._compute_quantity(move.product_uom_qty,pulsa_component_line.product_tmpl_parent_id.uom_id)
                    self.env['stock.move'].create({
                        'product_id': product.id,
                        'name': product.name,
                        'product_uom_qty': quantity,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.env.ref('stock.location_inventory').id,
                        'product_uom': pulsa_component_line.product_tmpl_parent_id.uom_id.id,
                        'origin': self.name,
                        'picking_id': picking_to_inventory_id.id
                    })
                    # stock
                    if not picking_to_stock_id:
                        picking_to_stock_id = self.env['stock.picking'].create(picking_vals_rev_to_stock)
                    product_to_stock = move.product_id
                    quantity_to_stock = move.product_uom._compute_quantity(move.product_uom_qty,product_to_stock.uom_id)
                    self.env['stock.move'].create({
                        'product_id': product_to_stock.id,
                        'name': product_to_stock.name,
                        'product_uom_qty': quantity_to_stock,
                        'location_id': self.env.ref('stock.location_inventory').id,
                        'location_dest_id': self.location_id.id,
                        'product_uom': product_to_stock.uom_id.id,
                        'origin': self.name,
                        'picking_id': picking_to_stock_id.id
                    })
            if picking_to_inventory_id and picking_to_inventory_id.move_lines:
                picking_to_inventory_id.action_confirm()
                picking_to_inventory_id.force_assign()
                picking_to_inventory_id.do_new_transfer()
                stock_transfer_id = self.env['stock.immediate.transfer'].search([('pick_id', '=', picking_to_inventory_id.id)],limit=1)
                stock_transfer_id.process()
                if picking_to_stock_id and picking_to_stock_id.move_lines:
                    picking_to_stock_id.action_confirm()
                    picking_to_stock_id.force_assign()
                    picking_to_stock_id.do_new_transfer()
                    stock_transfer_id = self.env['stock.immediate.transfer'].search(
                        [('pick_id', '=', picking_to_stock_id.id)], limit=1)
                    stock_transfer_id.process()

        return super(stock_picking,self).action_done()


# class StockImmediateTransfer(models.TransientModel):
#     _name = 'stock.immediate.transfer'


class PulsaComponentLine(models.Model):
    _name = 'pulsa.component.line'



    product_tmpl_parent_id = fields.Many2one('product.template')

    product_template_id = fields.Many2one('product.template', 'Product', required=True)
    # qty = fields.Integer(string='Quantity')
    balance = fields.Many2one('product.uom',string='Balance',related='product_template_id.uom_id',readonly=True)
