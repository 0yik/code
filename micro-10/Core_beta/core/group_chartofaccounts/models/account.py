# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Account(models.Model):
    _inherit = 'account.account'

    company_type = fields.Selection([('individual_company', 'Individual Company'), ('group_company', 'Group Company')], default='individual_company', string='Company Type')
    company_lines_ids = fields.One2many('company.lines', 'company_lines_id', string='Company Lines')

class CompanyLines(models.Model):
    _name = 'company.lines'

    @api.depends('account_id')
    def _get_account_code(self):
        for record in self:
            if record.company_lines_id and record.company_lines_id.company_type == 'group_company':
                record.code = record.account_id.code
            else:
                record.code = ''
                
    @api.depends('company_lines_id','company_lines_id.company_id')
    def _get_allowed_company_ids(self):
        for record in self:
            group_company_ids = []
            if (record.company_lines_id and record.company_lines_id.company_id) and (record.company_lines_id.company_id.company_type == 'group_company' and record.company_lines_id.company_id.company_line_ids):
                for line in record.company_lines_id.company_id.company_line_ids:
                    group_company_ids.append(line.company_id.id)
            if not group_company_ids:
                group_company_ids = [self.env.user.company_id.id]
            record.update({'allowed_company_ids': [(6,0,group_company_ids)]})

    @api.depends('company_id')
    def _get_company_percentage(self):
        for record in self:
            company_ids = self.env['company.line'].search([('company_id', '=', record.company_id.id)])
            if company_ids:
                record.percentage = company_ids.percentage
            else:
                record.percentage = 0

    company_id = fields.Many2one('res.company', string='Company')
    company_lines_id = fields.Many2one('account.account', string='Company Line')
    percentage = fields.Integer('Percentage Of Ownership',compute='_get_company_percentage',store=True)
    account_id = fields.Many2one('account.account',string='Account Name')
    code = fields.Char('Account Code',compute='_get_account_code',store=True)
    allowed_company_ids = fields.Many2many('res.company',compute='_get_allowed_company_ids', string='Allowed Companies',store=True)
    
CompanyLines()