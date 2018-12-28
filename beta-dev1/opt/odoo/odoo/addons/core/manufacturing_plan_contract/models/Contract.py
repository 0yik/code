# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class mrp_plan(models.Model):
    _inherit = 'mrp.plan'

    contract_id = fields.Many2one('account.analytic.account')

class add_mrp_order_wizard_line(models.Model):
    _inherit = 'mrp.order.wizard.line'

    add_id = fields.Many2one('mrp.order.wizard')
    product_id = fields.Many2one('product.product', "Product")
    quantity = fields.Integer('Quantity')
    contract_id = fields.Many2one('account.analytic.account')

class contract(models.Model):
    _inherit = 'account.analytic.account'

    product_order_ids = fields.One2many('mrp.order.wizard.line', 'contract_id')
    mrp_plan_id = fields.One2many('mrp.plan','contract_id')
    mrp_plan_count = fields.Integer(compute='_compute_mrp_plan_count', string='MRP Plan Count')

    def create_mrp_production_rescursive(self, move_raw_id):
        mrp_plan = self.mrp_plan_id
        MRP_PRDODUCTION = self.env['mrp.production']
        MRP_ORDER = self.env['mrp.order']
        product = move_raw_id.product_id
        product_uom_qty = move_raw_id.product_uom_qty
        if product.bom_ids:
            mrp_production_created_id = MRP_PRDODUCTION.create({
                'mrp_plan_id': mrp_plan.id,
                'product_id': product.id,
                'product_qty': product_uom_qty,
                'bom_id': product.bom_ids[0].id,
                'date_planned_start': datetime.now().strftime('%Y-%m-%d'),
                'user_id': self._uid,
                'product_uom_id': product.uom_id.id,
                'routing_id': product.bom_ids[0].routing_id and product.bom_ids[0].routing_id.id or False,
            })
            MRP_ORDER.create({
                'mrp_plan_id': mrp_plan.id,
                'mrp_production_id': mrp_production_created_id.id,
            })
            if mrp_production_created_id.move_raw_ids:
                for move_raw_id in mrp_production_created_id.move_raw_ids:
                    self.create_mrp_production_rescursive(move_raw_id)

    @api.multi
    def set_open(self):
        res = super(contract, self).set_open()
        MRP_PRDODUCTION = self.env['mrp.production']
        MRP_PLAN = self.env['mrp.plan']
        MRP_ORDER = self.env['mrp.order']
        mrp_plan = MRP_PLAN.create({
            'name' : self.name,
            'contract_id' : self.id,
            'date' : datetime.now().strftime('%Y-%m-%d'),
        })
        for line in self.product_order_ids:
            product = line.product_id
            qty = line.quantity
            # product_tmp = product.product_tmp_id
            if product.bom_ids:
                mrp_production_created_id = MRP_PRDODUCTION.create({
                    'mrp_plan_id': mrp_plan.id,
                    'product_id': product.id,
                    'product_qty': qty,
                    'bom_id': product.bom_ids[0].id,
                    'date_planned_start': datetime.now().strftime('%Y-%m-%d'),
                    'user_id': self._uid,
                    'product_uom_id': product.uom_id.id,
                    'routing_id': product.bom_ids[0].routing_id and product.bom_ids[0].routing_id.id or False,
                })
                MRP_ORDER.create({
                    'mrp_plan_id': mrp_plan.id,
                    'mrp_production_id': mrp_production_created_id.id,
                })
                if mrp_production_created_id.move_raw_ids:
                    for move_raw_id in mrp_production_created_id.move_raw_ids:
                        self.create_mrp_production_rescursive(move_raw_id)
        return res

    @api.multi
    def mrp_plans_action(self):
        mrp_plans = self.mapped('mrp_plan_id')
        result = {
            "type": "ir.actions.act_window",
            "res_model": "mrp.plan",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", mrp_plans.ids]],
            "context": {"create": False},
            "name": "mrp_plans",
        }
        if len(mrp_plans) == 1:
            result['views'] = [(False, "form")]
            result['res_id'] = mrp_plans.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result
    
    def _compute_mrp_plan_count(self):
        for account in self:
            account.mrp_plan_count = len(account.with_context(active_test=False).mrp_plan_id)