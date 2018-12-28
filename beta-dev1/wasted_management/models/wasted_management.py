# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WastedManagement(models.Model):
    _name = 'wasted.management'

    def _get_default_wasted_location_id(self):
        wasted_location_id = self.env['ir.model.data'].sudo().get_object('wasted_management', 'stock_location_wasted')
        return wasted_location_id

    def _get_default_location_id(self):
        return self.env.ref('stock.stock_location_stock', raise_if_not_found=False)

    name = fields.Char(
        'Reference', default=lambda self: _('New'),
        copy=False, readonly=True, required=True,
        states={'done': [('readonly', True)]})
    origin = fields.Char(string='Source Document')
    product_id = fields.Many2one(
        'product.product', 'Product',
        required=True, states={'done': [('readonly', True)]})
    product_uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure',
        required=True, states={'done': [('readonly', True)]})
    tracking = fields.Selection('Product Tracking', readonly=True, related="product_id.tracking")
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot',
        states={'done': [('readonly', True)]}, domain="[('product_id', '=', product_id)]")
    package_id = fields.Many2one(
        'stock.quant.package', 'Package',
        states={'done': [('readonly', True)]})
    owner_id = fields.Many2one('res.partner', 'Owner', states={'done': [('readonly', True)]})
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    picking_id = fields.Many2one('stock.picking', 'Picking', states={'done': [('readonly', True)]})
    location_id = fields.Many2one(
        'stock.location', 'Location', domain="[('usage', '=', 'internal')]",
        required=True, states={'done': [('readonly', True)]}, default=_get_default_location_id)
    wast_location_id = fields.Many2one(
        'stock.location', 'Wasted Location', default=_get_default_wasted_location_id,
        states={'done': [('readonly', True)]})  # domain="[('scrap_location', '=', True)]",
    wast_qty = fields.Float('Quantity', default=1.0, required=True, states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft',
        string='State', help='Various state of the Wast Management')
    date_expected = fields.Datetime('Expected Date', default=fields.Datetime.now)
    production_id = fields.Many2one(
        'mrp.production', 'Manufacturing Order',
        states={'done': [('readonly', True)]})
    workorder_id = fields.Many2one(
        'mrp.workorder', 'Work Order',
        states={'done': [('readonly', True)]},
        help='Not to restrict or prefer quants, but informative.')
    # employee_id = fields.Many2one('hr.employee', 'Approver', required=True, states={'done': [('readonly', True)]})
    machine_mgt_id = fields.Many2one('machine.management', 'MM Order')

    @api.onchange('workorder_id')
    def _onchange_workorder_id(self):
        if self.workorder_id:
            self.location_id = self.workorder_id.production_id.location_src_id.id

    @api.onchange('production_id')
    def _onchange_production_id(self):
        if self.production_id:
            self.location_id = self.production_id.move_raw_ids.filtered(lambda x: x.state not in (
                'done', 'cancel')) and self.production_id.location_src_id.id or self.production_id.location_dest_id.id,

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        if self.picking_id:
            self.location_id = (self.picking_id.state == 'done') and self.picking_id.location_dest_id.id or self.picking_id.location_id.id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('wasted.management') or _('New')
        wast = super(WastedManagement, self).create(vals)
        # wast.do_wast()
        return wast

    @api.multi
    def unlink(self):
        if 'done' in self.mapped('state'):
            raise UserError(_('You cannot delete a wast which is done.'))
        return super(WastedManagement, self).unlink()

    def _get_origin_moves(self):
        return self.picking_id and self.picking_id.move_lines.filtered(lambda
                                                                           x: x.product_id == self.product_id) or self.production_id and self.production_id.move_raw_ids.filtered(
            lambda x: x.product_id == self.product_id)

    #Code Moved To action_confirm
    # @api.multi
    # def do_wast(self):
        # for wast in self:
        #     moves = wast._get_origin_moves() or self.env['stock.move']
        #     move = self.env['stock.move'].create(wast._prepare_move_values())
        #     quants = self.env['stock.quant'].quants_get_preferred_domain(
        #         move.product_qty, move,
        #         domain=[
        #             ('qty', '>', 0),
        #             ('lot_id', '=', self.lot_id.id),
        #             ('package_id', '=', self.package_id.id)],
        #         preferred_domain_list=wast._get_preferred_domain())
        #     if any([not x[0] for x in quants]):
        #         raise UserError(_(
        #             'You cannot wast a move without having available stock for %s. You can correct it with an inventory adjustment.') % move.product_id.name)
        #     self.env['stock.quant'].quants_reserve(quants, move)
        #     move.action_done()
        #     wast.write({'move_id': move.id, 'state': 'draft'})#, 'state': 'done'
        #     moves.recalculate_move_state()
        # return True



    def _get_preferred_domain(self):
        if not self.picking_id:
            return []
        if self.picking_id.state == 'done':
            preferred_domain = [
                ('history_ids', 'in', self.picking_id.move_lines.filtered(lambda x: x.state == 'done')).ids]
            preferred_domain2 = [
                ('history_ids', 'not in', self.picking_id.move_lines.filtered(lambda x: x.state == 'done')).ids]
            return [preferred_domain, preferred_domain2]
        else:
            preferred_domain = [('reservation_id', 'in', self.picking_id.move_lines.ids)]
            preferred_domain2 = [('reservation_id', '=', False)]
            preferred_domain3 = ['&', ('reservation_id', 'not in', self.picking_id.move_lines.ids),
                                 ('reservation_id', '!=', False)]
            return [preferred_domain, preferred_domain2, preferred_domain3]
        if self.production_id:
            if self.product_id in self.production_id.move_raw_ids.mapped('product_id'):
                preferred_domain = [('reservation_id', 'in', self.production_id.move_raw_ids.ids)]
                preferred_domain2 = [('reservation_id', '=', False)]
                preferred_domain3 = ['&', ('reservation_id', 'not in', self.production_id.move_raw_ids.ids),
                                     ('reservation_id', '!=', False)]
                return [preferred_domain, preferred_domain2, preferred_domain3]
            elif self.product_id in self.production_id.move_finished_ids.mapped('product_id'):
                preferred_domain = [('history_ids', 'in', self.production_id.move_finished_ids.ids)]
                preferred_domain2 = [('history_ids', 'not in', self.production_id.move_finished_ids.ids)]
                return [preferred_domain, preferred_domain2]

    @api.multi
    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', '=', self.picking_id.id)]
        return action

    @api.multi
    def action_get_stock_move(self):
        action = self.env.ref('stock.stock_move_action').read([])[0]
        action['domain'] = [('id', '=', self.move_id.id)]
        return action



    @api.multi
    def action_confirm(self):
        for wast in self:
            moves = wast._get_origin_moves() or self.env['stock.move']
            move = self.env['stock.move'].create(wast._prepare_move_values())
            quants = self.env['stock.quant'].quants_get_preferred_domain(
                move.product_qty, move,
                domain=[
                    ('qty', '>', 0),
                    ('lot_id', '=', self.lot_id.id),
                    ('package_id', '=', self.package_id.id)],
                preferred_domain_list=wast._get_preferred_domain())
            if any([not x[0] for x in quants]):
                raise UserError(_(
                    'You cannot wast a move without having available stock for %s. You can correct it with an inventory adjustment.') % move.product_id.name)
            self.env['stock.quant'].quants_reserve(quants, move)
            move.action_done()
            wast.write({'move_id': move.id, 'state': 'done'})
            moves.recalculate_move_state()
        return True

    def _prepare_move_values(self):
        self.ensure_one()
        # added
        vals = {
            'name': self.name,
            'origin': self.origin or self.picking_id.name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.wast_qty,
            'location_id': self.location_id.id,
            # 'scrapped': True,
            'location_dest_id': self.wast_location_id.id,
            'restrict_lot_id': self.lot_id.id,
            'restrict_partner_id': self.owner_id.id,
            'picking_id': self.picking_id.id
        }
        if self.production_id:
            vals['origin'] = vals['origin'] or self.production_id.name
            if self.product_id in self.production_id.move_finished_ids.mapped('product_id'):
                vals.update({'production_id': self.production_id.id})
            else:
                vals.update({'raw_material_production_id': self.production_id.id})
        return vals

    @api.multi
    def action_done(self):
        return {'type': 'ir.actions.act_window_close'}

        # for obj in self:
        #     obj.write({'state': 'done'})
        #
        # return True

    # @api.multi
    # def to_approval(self):
    #     for obj in self:
    #         print "action to_approval", obj
    #         obj.write({'state': 'to_be_approved'})
    #     return True
    #
    # @api.multi
    # def action_approval(self):
    #     for obj in self:
    #         print "action approval", obj
    #         obj.write({'state': 'approved'})
    #     return True
    #
    # @api.multi
    # def action_reject(self):
    #     for obj in self:
    #         print "action reject", obj
    #         obj.write({'state': 'rejected'})
    #     return True
