# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partners(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')],
                                    default = 'company', readonly=False)
    customer_uen = fields.Char('Customer UEN')
    customer_id  = fields.Char('Customer ID')
    industry  = fields.Many2one('industry', 'Industry')

    @api.depends('is_company')
    def _compute_company_type(self):
        return None

    @api.onchange('company_type')
    def onchange_company_type(self):
        for record in self:
            if not record.company_type:
                record.company_type = 'company'
            company_type = record.company_type
            record.is_company = (record.company_type == 'company')
            record.company_type = company_type