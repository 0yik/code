# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    description = fields.Text('Description')


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    questionnaire_id = fields.Many2one('res.questionnaire.config', string='Questionnaire')
    response = fields.Text('Response')

