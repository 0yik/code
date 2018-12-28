# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    wast_ids = fields.One2many('wasted.management', 'workorder_id')
    wast_count = fields.Integer(compute='_compute_wast_move_count', string='Wasted Move')

    @api.multi
    def _compute_wast_move_count(self):
        data = self.env['wasted.management'].read_group([('workorder_id', 'in', self.ids)], ['workorder_id'],
                                                  ['workorder_id'])
        count_data = dict((item['workorder_id'][0], item['workorder_id_count']) for item in data)
        for workorder in self:
            workorder.wast_count = count_data.get(workorder.id, 0)

    @api.multi
    def button_wasted(self):
        self.ensure_one()
        machine_management_obj = self.env['machine.management'].search([('mrp_production_id','=', self.production_id and self.production_id.id or False), ('workcenter_id','=',self.workcenter_id and self.workcenter_id.id or False)])
        return {
            'name': _('Wasted'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wasted.management',
            'view_id': self.env.ref('wasted_management.wasted_management_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_workorder_id': self.id, 'default_production_id': self.production_id.id,
                        'default_machine_mgt_id': machine_management_obj.id,
                        'product_ids': (self.production_id.move_raw_ids.filtered(lambda x: x.state not in (
                        'done', 'cancel')) | self.production_id.move_finished_ids.filtered(
                            lambda x: x.state == 'done')).mapped('product_id').ids},
            'target': 'new',
        }

    @api.multi
    def action_see_move_wast(self):
        self.ensure_one()
        action = self.env.ref('wasted_management.action_wasted_management').read()[0]
        action['domain'] = [('workorder_id', '=', self.id)]
        return action