# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    phonecall_number = fields.Integer(compute='_compute_phonecall_total', string='Number of Phonecalls')
    phonecall_ids    = fields.One2many('crm.phonecall', 'opportunity_id', string='Phonecalls')

    @api.depends('phonecall_ids')
    def _compute_phonecall_total(self):
        for lead in self:
            phonecall_number      = len(lead.phonecall_ids.ids)
            lead.phonecall_number = phonecall_number