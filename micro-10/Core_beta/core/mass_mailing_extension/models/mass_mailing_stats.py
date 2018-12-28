# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class MailMailStats(models.Model):

    _inherit = 'mail.mail.statistics'
    
    recipient = fields.Char('Recipient')
    links_click_ids = fields.One2many('link.tracker.click', 'mail_stat_id', string='Links click')
