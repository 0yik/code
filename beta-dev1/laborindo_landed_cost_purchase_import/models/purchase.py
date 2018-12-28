# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
from datetime import datetime
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.depends('picking_ids','state')
    def _compute_is_picking_done(self):
        for rec in self:
            for picking in rec.picking_ids:
                if picking.state == 'done':
                    rec.is_picking_done = True

    @api.depends('order_line.move_ids')
    def _compute_lc(self):
        for order in self:
            lc_rec = self.env['stock.landed.cost'].search([('purchase_id','=',order.id)])
            if lc_rec:
                order.lc_ids = [(6, 0, lc_rec.ids)]
                order.lc_count = len(lc_rec)


    is_picking_done = fields.Boolean(string='Is Picking Done', compute="_compute_is_picking_done")
    lc_count = fields.Integer(compute='_compute_lc', string='Landed Cost Count', default=0)
    lc_ids = fields.Many2many('stock.picking', compute='_compute_lc', string='Landed Cost', copy=False)

    @api.multi
    def action_view_landed_cost(self):
        action = self.env.ref('stock_landed_costs.action_stock_landed_cost')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        lc_ids = sum([order.lc_ids.ids for order in self], [])
        # choose the view_mode accordingly
        if len(lc_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, lc_ids)) + "])]"
        elif len(lc_ids) == 1:
            res = self.env.ref('stock_landed_costs.view_stock_landed_cost_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = lc_ids and lc_ids[0] or False
        return result

class LandedCost(models.Model):

    _inherit = 'stock.landed.cost'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')

