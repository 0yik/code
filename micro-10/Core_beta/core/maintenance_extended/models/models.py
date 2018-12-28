# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    employee_ids = fields.Many2many('hr.employee',string="Employees")
    customer_id = fields.Many2one('res.partner', string="Customer")
    number = fields.Char('Number')

    @api.onchange('maintenance_team_id')
    def get_team(self):
        if self.maintenance_team_id:
            res=self.env['maintenance.team'].search([('id','=',self.maintenance_team_id.id)])
        if res:
            filb_values = [(6, 0, res.employee_ids.ids)]
            self.employee_ids=filb_values
        else:
            self.employee_ids=[]
    @api.onchange('stage_id')
    def onchange_stage_id_in_progress(self):
        if self.stage_id and self.stage_id.is_in_progress:
            self.number = self.env['ir.sequence'].next_by_code('maintenance.request')

    @api.multi
    def write(self, values):
        if self.maintenance_team_id:
            res=self.env['maintenance.team'].search([('id','=',self.maintenance_team_id.id)])
            if res:
                filb_values = [(6, 0, res.employee_ids.ids)]
                values['employee_ids']=filb_values
        res = super(MaintenanceRequest, self).write(values)
        if 'stage_id' in values:
            if self.stage_id.is_in_progress:
                self.number = self.env['ir.sequence'].next_by_code('maintenance.request')
        return res

MaintenanceRequest()

class MaintenanceExtender(models.Model):
    _inherit = 'maintenance.team'

    employee_ids = fields.Many2many('hr.employee',string="Employees")

    @api.multi
    def write(self, vals):
        res=super(MaintenanceExtender, self).write(vals)
        if 'employee_ids' in vals:
            obj=self.env['maintenance.request'].search([('maintenance_team_id','=',self.id)])
            for line in obj:
                line.write(vals)
        return res

class MaintenanceStage(models.Model):
    _inherit = 'maintenance.stage'

    is_in_progress = fields.Boolean('In Progress')

    @api.multi
    def write(self, vals):
        res = super(MaintenanceStage, self).write(vals)
        if res:
            for rec in self:
                if 'is_in_progress' in vals:
                    if vals['is_in_progress']:
                        mr_ids = rec.env['maintenance.request'].search([('stage_id', '=', rec.id)])
                        for mr in mr_ids:
                            mr.number = rec.env['ir.sequence'].next_by_code('maintenance.request')

        return res

class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    parent_id = fields.Many2one('maintenance.equipment.category', 'Parent Category')

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