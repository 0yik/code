# -*- coding: utf-8 -*-

from odoo import models, fields, api

class hr_empployee(models.Model):
    _inherit = 'hr.employee'

    branch_id = fields.Many2one('res.branch',string="Branch")
    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse")
    
