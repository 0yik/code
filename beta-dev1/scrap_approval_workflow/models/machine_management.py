# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID


class MachineManagement(models.Model):
    _inherit = 'machine.management'

    scrap_ids = fields.One2many('scrap.manufacturing', 'machine_mgt_id')
    scrap_count = fields.Integer(compute='_compute_scrap_move_count', string='Scrap Move')

    @api.multi
    def _compute_scrap_move_count(self):
        print '_compute_scrap_move_count',self,'production ids' ,self.mrp_production_id.ids,'scrap count',self.scrap_count

        data = self.env['scrap.manufacturing'].read_group([('machine_mgt_id', 'in', self.ids)], ['machine_mgt_id'],
                                                  ['machine_mgt_id'])
        count_data = dict((item['machine_mgt_id'][0], item['machine_mgt_id_count']) for item in data)
        for mmorder in self:
            mmorder.scrap_count = count_data.get(mmorder.id, 0)

    @api.multi
    def button_scrap(self):
        self.ensure_one()
        workorder_obj = self.env['mrp.workorder'].search(
            [('production_id', '=', self.mrp_production_id and self.mrp_production_id.id or False),
             ('workcenter_id', '=', self.workcenter_id and self.workcenter_id.id or False)])
        return {
            'name': _('Scrap Manufacturing'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'scrap.manufacturing',
            'view_id': self.env.ref('scrap_approval_workflow.scrap_manufacturing_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_workorder_id': workorder_obj.id, 'default_production_id': self.mrp_production_id.id,
                        'default_machine_mgt_id': self.id,
                        'product_ids': (self.mrp_production_id.move_raw_ids.filtered(lambda x: x.state not in (
                        'done', 'cancel')) | self.mrp_production_id.move_finished_ids.filtered(
                            lambda x: x.state == 'done')).mapped('product_id').ids},
            'target': 'new',
        }

    @api.multi
    def action_see_move_scrap(self):
        self.ensure_one()
        action = self.env.ref('scrap_approval_workflow.action_scrap_manufacturing').read()[0]
        action['domain'] = [('machine_mgt_id', '=', self.id)]
        return action