# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Company(models.Model):
    _inherit = 'res.company'

    company_type = fields.Selection([('individual_company','Individual Company'),('group_company','Group Company')], default='individual_company', string='Company Type')
    company_line_ids = fields.One2many('company.line','company_line_id',string='Company Lines')

Company()

class CompanyLine(models.Model):
    _name = 'company.line'

    company_id = fields.Many2one('res.company',string='Company')
    company_line_id = fields.Many2one('res.company',string='Company Line')
    percentage = fields.Integer('Percentage Of Ownership')

    @api.onchange('percentage')
    def onchange_check_percentage(self):
        warning = {}
        if self.percentage and (self.percentage < 0 or self.percentage > 100):
            self.percentage = False
            warning = {'title': 'Value Error', 'message': "Percentage should be between 0 to 100!!!"}
        return {'warning': warning}

CompanyLine()