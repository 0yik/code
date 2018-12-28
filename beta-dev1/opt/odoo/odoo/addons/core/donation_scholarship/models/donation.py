# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Donation(models.Model):
    _inherit = 'donation'

    use_scholarship = fields.Boolean('Use as Scholarship')
    no_of_scholarship = fields.Integer('Number of Scholarship Available', default=1)
    scholarship_id = fields.Many2one('scholarship', string='Scholarships', copy=False)
    scholarship_given = fields.Integer(string='Scholarship Given')
    scholarship_balance = fields.Integer(string='Scholarship Amount Balance')

    @api.multi
    def button_confirm(self):
        super(Donation, self).button_confirm()
        if self.use_scholarship:
            vals = {}
            vals['name'] = self.partner_id.name + ' Scholarship'
            vals['provider'] = self.partner_id.name
            vals['currency_id'] = self.currency_id.id
            vals['amount'] = self.amount / self.no_of_scholarship
            vals['quantity'] = self.no_of_scholarship
            scholarship_id = self.env['scholarship'].create(vals)
            self.scholarship_id = scholarship_id.id
            action = self.env.ref('scholarship_management.action_scholarship').read()[0]
            action['views'] = [(False, 'form')]
            action['res_id'] = scholarship_id.id
            return action

    @api.multi
    def action_view_scholarship(self):
        action = self.env.ref('scholarship_management.action_scholarship').read()[0]
        action['views'] = [(False, 'form')]
        action['res_id'] = self.scholarship_id.id
        return action

Donation()

class ScholarshipApplication(models.Model):
    _inherit = 'scholarship.application'

    @api.multi
    def button_approve(self):
        super(ScholarshipApplication, self).button_approve()
        donation_ids = self.env['donation'].search([('scholarship_id','=',self.scholarship_id.id)], limit=1)
        if donation_ids:
            application_ids = self.env['scholarship.application'].search([('scholarship_id','=',self.scholarship_id.id),('state','=','approve')]).ids
            donation_ids.scholarship_given = len(application_ids)
            donation_ids.scholarship_balance = self.scholarship_id.quantity * len(application_ids)
        return True

ScholarshipApplication()