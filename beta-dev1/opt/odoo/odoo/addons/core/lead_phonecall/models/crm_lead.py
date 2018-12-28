# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def _compute_phonecall_count(self):
        print '-call----------'
        phonecall = self.env['crm.phonecall'].search([('opportunity_id', '=', self.id)])
        print '--------phonecall-------', phonecall, phonecall
        self.phonecall_count = len(phonecall.ids)

    phonecall_count = fields.Integer(string="# PhoneCalls", compute='_compute_phonecall_count')

    @api.multi
    def action_schedule_phonecall(self):
        print '----------6666666---------------'
        self.ensure_one()
        phonecall = self.env['crm.phonecall'].search([('opportunity_id', '=', self.id)])
        action = self.env.ref('crm_phonecall.crm_case_categ_phone0').read()[0]
        action['res_id'] = phonecall.ids
        action['domain'] = [['id', 'in', phonecall.ids]]
        action['context'] = {
            'default_opportunity_id': self.id
        }
        print '------action--------', action
        return action


