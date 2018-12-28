# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrContract(models.Model):
    _inherit = "hr.contract"
    
    @api.multi
    def _get_increment(self):
        for contract in self:
            record = self.env['hr.contract'].search([('date_end', '<', contract.date_end),('employee_id', '=', contract.employee_id.id)], order='date_end DESC',limit=1)
            if record:
                value = contract.wage-record.wage
                contract.increment = value
    increment = fields.Float(compute='_get_increment', type='float', string="Increment")
    