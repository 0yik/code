# coding=utf-8
from odoo import api, fields, models, _


class PurchasOrderModification(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _compute_landed_cost(self):
        for cost in self:
            costs = self.env['stock.landed.cost'].search([('source_reference','=',cost.name)])
            cost.landed_cost_ids = costs
            cost.landed_cost_count = len(costs)

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_is_shipped_done(self):
        for order in self:
            print "order.picking_ids",order.picking_ids
            if order.picking_ids and all([x.state in ('done','tracking') for x in order.picking_ids]):
                order.is_shipping_done = True
                print "order.is_shipping_done",order.is_shipping_done

    landed_cost_count = fields.Integer(compute='_compute_landed_cost', string='Receptions', default=0)
    landed_cost_ids = fields.Many2many('stock.landed.cost', compute='_compute_landed_cost', string='Landed Costs', copy=False)
    is_shipping_done = fields.Boolean(compute='_compute_is_shipped_done')

    def action_landed_cost_wiz(self):
        landed_cost_form = self.env.ref('landed_cost_purchase_import.purchase_landed_cost_wizard', False)
        res = {}
        if landed_cost_form:
            res = {'name': ('Landed Costs'),
                   'type': 'ir.actions.act_window',
                   'view_type': 'form',
                   'view_mode': 'form',
                   'res_model': 'landed.cost.purchase',
                   'view_id': landed_cost_form.id,
                   'target': 'new',
                   'context': {'default_order_id': self.id}}
        return res

    # def action_view_landed_cost(self):
    #
    #     costs_id = self.env['stock.landed.cost'].search([('source_reference','=',self.name)])
    #     # action = self.env.ref('mrp.mrp_production_tree_view').read()[0]
    #     res = {}
    #     if len(costs_id) > 1:
    #         view_ref = self.env['ir.model.data'].get_object_reference('stock_landed_costs', 'view_stock_landed_cost_tree')
    #         res['domain'] = [('id', 'in', costs_id.ids)]
    #         res['view_mode'] = 'tree'
    #     elif len(costs_id) == 1:
    #         view_ref = self.env['ir.model.data'].get_object_reference('stock_landed_costs', 'view_stock_landed_cost_form')
    #         res['res_id'] = costs_id.ids[0]
    #         res['view_mode'] = 'form'
    #
    #     view_id = view_ref[1] if view_ref else False
    #     res.update({
    #         'type': 'ir.actions.act_window',
    #         'name': _('Landed Costs'),
    #         'res_model': 'stock.landed.cost',
    #         # 'view_type': 'tree,form',
    #         'view_id': view_id,
    #         # 'view_mode' : res['view_mode'],
    #         'target': 'current',
    #     })
    #     return res

    @api.multi
    def action_view_landed_cost(self):
        action = self.env.ref('stock_landed_costs.action_stock_landed_cost').read()[0]
        unit_ids = self.env['stock.landed.cost'].search([('source_reference', '=', self.name)]).sudo().ids
        if len(unit_ids) > 1:
            action['domain'] = [('id', 'in', unit_ids)]
        elif len(unit_ids) == 1:
            action['domain'] = [('id', 'in', unit_ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

class LandedCostModification(models.Model):
    _inherit = 'stock.landed.cost'

    source_reference = fields.Char(string='Source Reference')
    attachment = fields.Binary('Attachment')
    
    @api.model
    def create(self,vals):
        if self._context and self._context.get('default_order_id'):
            print "context",self._context.get('default_order_id')
            purchase_obj = self.env['purchase.order'].browse(self._context.get('default_order_id'))
            print "Purchase name",purchase_obj.name
            vals['source_reference'] = purchase_obj.name
        else:
            vals['source_reference'] = ''
        res = super(LandedCostModification, self).create(vals)
        return res