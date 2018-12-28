# -*- coding: utf-8 -*-

from odoo import models, fields, api


class project_booking(models.Model):
    
    _inherit = 'project.booking'
    
    feedback_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ])
    feedback_description = fields.Text()
    feedback_received = fields.Boolean()
    
    @api.multi
    def write(self, vals):
        res = super(project_booking, self).write(vals)
        if vals.get('status') == 'completed':
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            for rec in self:
                template = self.env.ref('hilti_website_feedback.mail_template_booking_feedback')
                template.with_context(feedback_url=base_url+'/booking_feedback?id=' + str(rec.id)).send_mail(rec.id, force_send=True)
        return res 