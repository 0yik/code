# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _get_default_currency_id(self):
        if self.company_id and self.company_id.currency_id and self.company_id.currency_id.id:
            self.currency_id = self.company_id.currency_id.id


    project_number = fields.Char('Project Number')
    currency_id = fields.Many2one(string="Contract Currency", default=_get_default_currency_id)

    business_partner = fields.Char('Business Partner')
    business_partner_number = fields.Char('Business Partner Number')
    end_user = fields.Char('End User')
    contract_amount = fields.Float('Contract Amount')
    project_hedging = fields.Char('Project Hedging')
    business_segment = fields.Many2one('account.business.segment','Business Segment')
    team_members = fields.One2many('account.team.member', 'account_analytic_id', 'Team Members')

class business_segment(models.Model):
    _name = 'account.business.segment'
    _description = 'Business Segment'

    name = fields.Char('Name')

class account_team_member(models.Model):
    _name = 'account.team.member'

    name = fields.Char('Name')
    account_analytic_id = fields.Many2one('account.analytic.account', 'Account Analytic ID', ondelete='cascade', required=True)
    user_id = fields.Many2one('res.users', 'Users')
    roles = fields.Char('Roles')
    status = fields.Selection([('active', 'Active'),('inactive', 'Inactive')], string='Status')