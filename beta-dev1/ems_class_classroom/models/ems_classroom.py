# -*- coding: utf-8 -*-
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError

class EmsClassRoom(models.Model):
    _name = 'ems.classroom'
    _description = "Class Room"
    
    name = fields.Char('Name', required=True)
    capacity = fields.Integer('Capacity',required=True)
    equipment_id = fields.Many2one('ems.equipment','Equipment')
    description = fields.Text('Description')
    date = fields.Date('Date')
    
    equipment_ids = fields.Many2many('ems.equipment', 'ems_equipment_rel', 'classroom_id', 'equipment_id', string="Equipments")
    
class Equipment(models.Model):
    _name = 'ems.equipment'
    _description = "Equipment"
    
    name = fields.Char('Name', required=True)

    
