# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID


class MachineManagement(models.Model):
    _inherit = 'machine.management'

    wast_ids = fields.One2many('wasted.management', 'machine_mgt_id')
    wast_count = fields.Integer(compute='_compute_wast_move_count', string='Wasted Move')

    @api.multi
    def _compute_wast_move_count(self):

        data = self.env['wasted.management'].read_group([('machine_mgt_id', 'in', self.ids)], ['machine_mgt_id'],
                                                        ['machine_mgt_id'])
        count_data = dict((item['machine_mgt_id'][0], item['machine_mgt_id_count']) for item in data)
        for mmorder in self:
            mmorder.wast_count = count_data.get(mmorder.id, 0)

    @api.multi
    def button_wasted(self):
        self.ensure_one()
        workorder_obj = self.env['mrp.workorder'].search([('production_id','=',self.mrp_production_id and self.mrp_production_id.id or False), ('workcenter_id','=',self.workcenter_id and self.workcenter_id.id or False)])
        return {
            'name': _('Wasted'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wasted.management',
            'view_id': self.env.ref('wasted_management.wasted_management_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_workorder_id': workorder_obj.id, 'default_production_id': self.mrp_production_id.id,
                        'default_machine_mgt_id': self.id,
                        'product_ids': (self.mrp_production_id.move_raw_ids.filtered(lambda x: x.state not in (
                            'done', 'cancel')) | self.mrp_production_id.move_finished_ids.filtered(
                            lambda x: x.state == 'done')).mapped('product_id').ids},
            'target': 'new',
        }

    @api.multi
    def action_see_move_wast(self):
        self.ensure_one()
        action = self.env.ref('wasted_management.action_wasted_management').read()[0]
        action['domain'] = [('machine_mgt_id', '=', self.id)]
        return action
