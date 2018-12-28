# -*- coding: utf-8 -*-

from odoo import models, fields, api


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_create_work_order(self):
        orders_to_plan = self.filtered(lambda order: order.state == 'confirmed')
        for record in self:
            record.general_workorders_from_mo()
        return orders_to_plan.write({'state': 'planned'})

    @api.model
    def general_workorders_from_mo(self):
        workorders = self.env['mrp.workorder']
        recipe_obj = self.env['mrp.bom.recipe']
        processed_order = []
        if self.bom_id and self.bom_id.recipe_ids:
            if self.product_id.tracking == 'serial':
                quantity = 1.0
            else:
                quantity = self.product_qty - sum(self.move_finished_ids.mapped('quantity_done'))
                quantity = quantity if (quantity > 0) else 0
            first_step_seq = 0
            sequence = 0
            recipe_ids = recipe_obj.search([('id', 'in', self.bom_id.recipe_ids.ids)],order='step_seq')
            while len(recipe_ids) > 0 :
                recipe_id = recipe_ids[0]
                same_seq_ids = recipe_ids.filtered(lambda x: x.step_seq == recipe_id.step_seq)
                recipe_ids -= same_seq_ids
                for recipe in same_seq_ids:
                    state = 'pending'
                    if len(workorders) == 0:
                        first_step_seq = recipe.step_seq
                        state = 'ready'
                    else:
                        if recipe.step_seq == first_step_seq:
                            state = 'ready'

                    workorder = workorders.create({
                        'name': recipe.name,
                        'production_id': self.id,
                        'workcenter_id': recipe.work_center.id,
                        'state': state,
                        'qty_producing': quantity,
                        'capacity': recipe.work_center.capacity,
                        'sequence' : sequence,
                        'recipe_id' : recipe.id,
                    })
                    workorders += workorder
                sequence +=1
        return workorders

class mrp_workorders(models.Model):
    _inherit = 'mrp.workorder'

    sequence = fields.Integer('Sequence')
    recipe_id = fields.Many2one('mrp.bom.recipe', string='Recipe ID')

    @api.multi
    def write(self, vals):
        res = super(mrp_workorders, self).write(vals)
        if vals.get('state',False) == 'done':
            self.compute_state()
        return res

    @api.model
    def compute_state(self):
        production_obj = self.env['mrp.production']
        for record in self:
            if record.production_id and record.production_id.id and record.state == 'done':
                related_orders = self.search([('production_id','=', record.production_id.id)])
                order_done_ids = related_orders.filtered(lambda r: r.state != 'done' and r.sequence == record.sequence)
                if len(order_done_ids) == 0:
                    next_order = related_orders.filtered(lambda x: x.sequence == (record.sequence + 1))
                    next_order.write({'state' : 'ready'})


