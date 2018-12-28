# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MassMailing(models.Model):

    _inherit = 'mail.mass_mailing'
    
    schedule_ok = fields.Boolean('Scheduled')
    click_ratio = fields.Integer('Clicks Ratio', compute="_compute_clicks", store=True)
    clicks_count = fields.Integer('Clicks Count', compute="_compute_clicks", store=True)
    link_ids = fields.One2many('link.tracker', 'mass_mailing_id', 'Links')
    
    @api.one
    @api.depends('statistics_ids', 'statistics_ids.links_click_ids', 'statistics_ids.mass_mailing_id', 'link_ids', 
        'link_ids.mass_mailing_id', 'link_ids.link_click_ids')
    def _compute_clicks(self):
        link_ids = self.env['link.tracker'].search([('mass_mailing_id', '=', self.id)])
        link_count = len(link_ids)
        mail_ids = self.env['mail.mail.statistics'].search([('mass_mailing_id', '=', self.id)])
        mail_count = len(mail_ids)
        total_links = mail_count*link_count
        click_ratio = 0.0
        click_count = 0
        if total_links:
            click_count = link_ids and sum([link.count for link in link_ids]) or 0
            click_ratio = 100 * (float(click_count)/total_links)
        self.click_ratio = click_ratio
        self.clicks_count = click_count
        
    @api.multi
    def schedule_mail(self):
        if not self.schedule_date:
            raise UserError(_('Please Enter Scheduled Date !!'))
        self.write({'schedule_ok': True, 'state': 'in_queue'})
    
    @api.model
    def _process_mass_mailing_queue(self):
        mass_mailings = self.search([('state', 'in', ('in_queue', 'sending')), '|', ('schedule_date', '<', fields.Datetime.now()), ('schedule_date', '=', False)])
        for mass_mailing in mass_mailings:
            if len(mass_mailing.get_remaining_recipients()) > 0:
                mass_mailing.state = 'sending'
                mass_mailing.send_mail()
            else:
                mass_mailing.state = 'done'

    @api.onchange('mailing_model', 'contact_list_ids')
    def _onchange_model_and_list(self):
        if not self._context.get('preview_of_mail'):
            if self.mailing_model == 'mail.mass_mailing.contact':
                if self.contact_list_ids:
                    self.mailing_domain = "[('list_id', 'in', %s), ('opt_out', '=', False)]" % self.contact_list_ids.ids
                else:
                    self.mailing_domain = "[('list_id', '=', False)]"
            elif 'opt_out' in self.env[self.mailing_model]._fields:
                self.mailing_domain = "[('opt_out', '=', False)]"
            else:
                self.mailing_domain = []
            self.body_html = "on_change_model_and_list"



    