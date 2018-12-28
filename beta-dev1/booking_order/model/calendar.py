
from odoo import models, fields, api

class Lot(models.Model):
	_inherit='stock.production.lot'

	calendar_id=fields.Many2one('calendar.event')

class Calendar(models.Model):
    _inherit = "calendar.event"
    
    equipment_ids = fields.One2many('stock.production.lot','calendar_id', 'Equipment')
    employee_id = fields.Many2one('hr.employee','Employee')
    serial_number_id = fields.Many2one("stock.production.lot",string = "Serial Numbers")