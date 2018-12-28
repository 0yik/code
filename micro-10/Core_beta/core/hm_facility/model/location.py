# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class Location(models.Model):
    _name = 'location'
    _inherit = ['mail.thread']

    name = fields.Char(string='Location',required=True)
    parent_id = fields.Many2one('location', "Parent Location")
    facility_ids = fields.One2many('maintenance.equipment', 'location_id')
    facility_count = fields.Integer('#Facility', compute='compute_facility_count')

    @api.depends('facility_ids')
    @api.multi
    def compute_facility_count(self):
        for rec in self:
            rec.facility_count = len(rec.facility_ids)

    @api.multi
    def action_view_facility(self):
        if self.facility_count > 1:
            return {
                'name': _('Facility'),
                'view_mode': 'kanban,tree,form',
                'view_type': 'form',
                # 'view_id': self.env.ref('maintenance_job_order.job_order_view_kanban').id,
                'res_model': 'maintenance.equipment',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.facility_ids.ids)]
            }
        else:
            return {
                'name': _('Facility'),
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('maintenance.hr_equipment_view_form').id,
                'res_model': 'maintenance.equipment',
                'type': 'ir.actions.act_window',
                'res_id': self.facility_ids[0].id
            }
        
    @api.multi
    def name_get(self):
        res = []
        for category in self:
            names = [category.name]
            parent_category = category.parent_id
            while parent_category:
                names.append(parent_category.name)
                parent_category = parent_category.parent_id
            res.append((category.id, ' / '.join(reversed(names))))
        return res

Location()