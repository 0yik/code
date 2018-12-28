# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_utils

class Inventory(models.Model):
    _inherit = "stock.inventory"
    _description = "Inventory"

    source = fields.Char('Source Document')

class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    _description = "Inventory Line"

    @api.model
    def create(self, values):
        if 'product_id' in values and 'product_uom_id' not in values:
            values['product_uom_id'] = self.env['product.product'].browse(values['product_id']).uom_id.id
        try:
            self = super(InventoryLine, self).create(values)
        except UserError as e:
            if not values.get('created_from_purchase'):
                raise e
            return self            
        except Exception as e:
            raise e
        return self

    @api.multi
    @api.depends('theoretical_qty', 'original_received_qty')
    def _get_adjusted_real_qunatity(self):
        for record in self:
            record.adjusted_qty = record.theoretical_qty - record.original_received_qty
            record.product_qty = record.product_id.qty_available

    @api.one
    @api.depends('location_id', 'product_id', 'package_id', 'product_uom_id', 'company_id', 'prod_lot_id', 'partner_id')
    def _compute_theoretical_qty(self):
        if self.created_from_purchase:
            self.theoretical_qty = self.purchased_qty
        else:
            super(InventoryLine, self)._compute_theoretical_qty()

    original_received_qty = fields.Float(
        'Original Received Quantity',
        digits=dp.get_precision('Product Unit of Measure'), default=0)
    adjusted_qty = fields.Float(
        'Adjusted Quantity',
        digits=dp.get_precision('Product Unit of Measure'), compute=_get_adjusted_real_qunatity)
    product_qty = fields.Float(
        'Checked Quantity',
        digits=dp.get_precision('Product Unit of Measure'), compute=_get_adjusted_real_qunatity)
    created_from_purchase = fields.Boolean('Created From Purchase')
    purchased_qty = fields.Float(
        'Purchased Quantity',
        digits=dp.get_precision('Product Unit of Measure'))

    def _generate_moves(self):
        moves = self.env['stock.move']
        Quant = self.env['stock.quant']
        for line in self.filtered(lambda l:l.created_from_purchase):
            line._fixup_negative_quants()

            if float_utils.float_compare(line.theoretical_qty, line.original_received_qty, precision_rounding=line.product_id.uom_id.rounding) == 0:
                continue
            if line.adjusted_qty < 0:  # found more than expected
                vals = self._get_move_values(abs(line.adjusted_qty), line.product_id.property_stock_inventory.id, line.location_id.id)
            else:
                vals = self._get_move_values(abs(line.adjusted_qty), line.location_id.id, line.product_id.property_stock_inventory.id)
            move = moves.create(vals)

            if line.adjusted_qty > 0:
                domain = [('qty', '>', 0.0), ('package_id', '=', line.package_id.id), ('lot_id', '=', line.prod_lot_id.id), ('location_id', '=', line.location_id.id)]
                preferred_domain_list = [[('reservation_id', '=', False)], [('reservation_id.inventory_id', '!=', line.inventory_id.id)]]
                quants = Quant.quants_get_preferred_domain(move.product_qty, move, domain=domain, preferred_domain_list=preferred_domain_list)
                Quant.quants_reserve(quants, move)
            elif line.package_id:
                move.action_done()
                move.quant_ids.write({'package_id': line.package_id.id})
                quants = Quant.search([('qty', '<', 0.0), ('product_id', '=', move.product_id.id),
                                       ('location_id', '=', move.location_dest_id.id), ('package_id', '!=', False)], limit=1)
                if quants:
                    for quant in move.quant_ids:
                        if quant.location_id.id == move.location_dest_id.id:  #To avoid we take a quant that was reconcile already
                            quant._quant_reconcile_negative(move)
        moves = super(InventoryLine, self.filtered(lambda l:not l.created_from_purchase))
        return moves

class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_transfer(self):
        res = super(Picking, self).do_transfer()
        for record in self:
            moves = record.move_lines.filtered(lambda l: not l.move_dest_id)
            if record.state=='done' and record.location_dest_id.usage == 'internal' and record.picking_type_id.code in ['incoming', 'internal'] and moves:
                po = self.env['purchase.order'].search([('name', '=', record.origin)])
                if po:
                    lines = []
                    for move in record.move_lines:
                        quant = move.quant_ids.filtered(lambda q: q.location_id==move.location_dest_id and q.product_id==move.product_id)
                        lines.append((0, 0, {
                                'product_id': move.product_id.id,
                                'product_uom_id': move.product_uom.id,
                                'location_id': move.location_dest_id.id,
                                'created_from_purchase': True,
                                'purchased_qty': move.product_uom_qty,
                                'partner_id': move.restrict_partner_id.id or record.partner_id.id,
                                'prod_lot_id': move.restrict_lot_id.id,
                                'package_id': quant and quant[0].package_id.id or False,
                                'original_received_qty': move.product_uom_qty,
                            }))
                    inventory = self.env['stock.inventory'].create({
                    'filter':'partial',
                    'source':record.name,
                    'line_ids':lines,
                    'name':'Inventory for '+record.name
                    })
                    inventory.prepare_inventory()
        return res



        

