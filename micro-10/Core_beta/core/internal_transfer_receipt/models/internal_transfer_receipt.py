# -*- coding: utf-8 -*-
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class InternalTransfer(models.Model):
    _name = 'internal.transfer'
    
    name = fields.Char('Name', default="/")
    partner_id = fields.Many2one('res.partner', string="Partner")
    schedule_date = fields.Date('Scheduled Date', default=datetime.today())
    source_loc_id = fields.Many2one('stock.location', 'Source Location')
    dest_loc_id = fields.Many2one('stock.location', 'Destination Location')
    product_line_ids = fields.One2many('internal.transfer.line', 'transfer_id', string="Transfer")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], string="State", default='draft')
    picking_ids = fields.One2many('stock.picking', 'transfer_id', string="Picking Operations")
    picking_count = fields.Integer(compute="_compute_picking_count", string="Picking Count")

    @api.multi
    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for transfer in self:
            transfer.picking_count = len(transfer.picking_ids)
    
    @api.model
    def create(self, vals):
        res = super(InternalTransfer, self).create(vals)
        if res.name == '/':
            res.name = self.env['ir.sequence'].next_by_code('internal.transfer')
        return res

    @api.multi
    def unlink(self):
        for transfer in self:
            if transfer.state=='confirm':
                raise UserError('You can not delete record in Confirm stage')
        return super(InternalTransfer, self).unlink()

    @api.multi
    def button_confirm(self):
        for transfer in self:
            if not transfer.product_line_ids:
                raise UserError("Please add product lines")
            stock_move_obj = self.env['stock.move']
            transit_location = self.env['stock.location'].search([('usage','=','transit'),('company_id','=',self.env.user.company_id.id)], limit=1)
            do_data = {
                'location_id': transfer.source_loc_id.id,
                'location_dest_id': transit_location.id,
                'move_type': 'direct',
                'partner_id':transfer.partner_id.id,
                'min_date': transfer.schedule_date,
#                 'name' : 'DO ' + transfer.name,
                'picking_type_id': self.env['stock.picking.type'].search([('code','=','outgoing')], limit=1).id,
                'origin':transfer.name,
                'transfer_id':transfer.id
            }
            do_picking = self.env['stock.picking'].create(do_data)
            receipt_data = {
                'location_id': transit_location.id,
                'location_dest_id': transfer.dest_loc_id.id,
                'move_type': 'direct',
                'partner_id':transfer.partner_id.id,
                'min_date': transfer.schedule_date,
#                 'name' : 'Receipt ' + transfer.name,
                'picking_type_id': self.env['stock.picking.type'].search([('code','=','incoming')], limit=1).id,
                'origin':transfer.name,
                'transfer_id':transfer.id
            }
            receipt_picking = self.env['stock.picking'].create(receipt_data)
            for line in transfer.product_line_ids:
                do_move_data = {
                    'picking_id': do_picking.id,
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty':line.product_uom_qty,
                    'product_uom': line.uom_id.id,
                    'location_id': transfer.source_loc_id.id,
                    'location_dest_id': transit_location.id,
                    'date_expected':transfer.schedule_date or datetime.today().date(),
                }
                stock_move_obj.create(do_move_data)
                receipt_move_data = {
                    'picking_id': receipt_picking.id,
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.uom_id.id,
                    'location_id': transit_location.id,
                    'location_dest_id': transfer.dest_loc_id.id,
                    'date_expected':transfer.schedule_date or datetime.today().date(),
                }
                stock_move_obj.create(receipt_move_data)
            transfer.write({'state':'confirm'})
            return True
        
    @api.multi
    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given internal transfer. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''

        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('transfer_id', '=', self.id)]
        return action

class InternalTransferLine(models.Model):
    _name = 'internal.transfer.line'

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the line.
        """
        for line in self:
            price = line.price_unit * line.product_uom_qty
            line.update({
                'price_total': price,
            })

    name = fields.Char('Description', required=False)
    product_id = fields.Many2one('product.product', string="Product")
#     price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', readonly=True, store=True)
    product_uom_qty = fields.Float(string='Quantity', default="1.0")
    sequence = fields.Integer(string='Sequence', default=10)
    transfer_id = fields.Many2one('internal.transfer', string='Transfer Reference', ondelete='cascade', copy=False)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')

    @api.onchange('product_id')
    def product_id_change(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price or 0.0
            self.uom_id = self.product_id.uom_id.id
            
class StockPikcing(models.Model):
    _inherit = 'stock.picking'
    
    transfer_id = fields.Many2one('internal.transfer', string='Internal Transfer')
    