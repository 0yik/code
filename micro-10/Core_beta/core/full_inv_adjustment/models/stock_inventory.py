# -*- coding: utf-8 -*-
from odoo import api, fields, models
from collections import defaultdict

class Inventory(models.Model):
    _inherit = 'stock.inventory'

    new_price = fields.Boolean('Value with new Unit Price')


class InventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    @api.depends('product_qty','theoretical_qty')
    def compute_changes(self):
        for record in self:
            record.change = record.product_qty - record.theoretical_qty

    unit_price = fields.Float('Unit Price')
    new_price = fields.Boolean('Value with new Unit Price', related='inventory_id.new_price')
    change = fields.Float(compute='compute_changes', string='Changes', store=True)


    def _get_move_values(self, qty, location_id, location_dest_id):
        res = super(InventoryLine, self)._get_move_values(qty, location_id, location_dest_id)
        res.update({
            'price_unit': self.unit_price,
        })
        return res


class stock_move(models.Model):
    
    _inherit = 'stock.move'
         
    @api.multi
    def product_price_update_after_done(self):
        ''' Adapt standard price on outgoing moves, so that a
        return or an inventory loss is made using the last value used for an outgoing valuation. '''
        to_update_moves = self.filtered(lambda move: move.location_dest_id.usage != 'internal')
        for move in to_update_moves:
            if move.inventory_id.new_price > 0.00:
                line_id = self.env['stock.inventory.line'].search([('product_id', '=', move.product_id.id), ('inventory_id', '=', move.inventory_id.id)], limit=1)
                move.write({'price_unit': line_id.unit_price})
            else:
                move._store_average_cost_price()
                
    def set_default_price_unit_from_product(self):
        """ Set price to move, important in inter-company moves or receipts with only one partner """
        for move in self._set_default_price_moves():
            if move.inventory_id and move.inventory_id.new_price > 0.00:
                line_id = self.env['stock.inventory.line'].search([('product_id', '=', move.product_id.id), ('inventory_id', '=', move.inventory_id.id)], limit=1)
                move.write({'price_unit': line_id.unit_price})
            else:
                move.write({'price_unit': move.product_id.standard_price})

class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _create_account_move_line(self, move, credit_account_id, debit_account_id, journal_id):
        # group quants by cost
        quant_cost_qty = defaultdict(lambda: 0.0)

        for quant in self:
            if move.inventory_id.new_price:
                for inv_line in move.inventory_id.line_ids:
                    invetory_line = inv_line.search([('product_id', '=', move.product_id.id), ('id', '=', inv_line.id)])
                    quant_cost_qty[invetory_line.unit_price] += quant.qty
            else:
                quant_cost_qty[quant.cost] += quant.qty

        AccountMove = self.env['account.move']
        for cost, qty in quant_cost_qty.iteritems():
            move_lines = move._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
            if move_lines:
                date = self._context.get('force_period_date', fields.Date.context_today(self))
                new_account_move = AccountMove.create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': move.picking_id.name})
                new_account_move.post()

