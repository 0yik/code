# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import Warning


class TestingDelay(models.TransientModel):
    _name = 'testing.delay'
    
    delay_time = fields.Float('Delay Duration')
    delay_remark = fields.Text('Delay Remarks')
    
    
    def add_delay(self):
        pr_book = self.env['project.booking'].browse(self._context.get('active_ids', []))
        pr_book.add_delay(self.delay_time, self.delay_remark)
        return True


class project_booking_anchor(models.Model):
    
    _inherit = 'project.booking.anchor'
    
    feedback_id = fields.Many2one('testing.feedback')


class TestingFeedback(models.Model):
    _name = 'testing.feedback'
    
    
    def _default_anchor(self):
        
        
        booking = self.env['project.booking'].search([('id', '=', self._context.get('active_id'))])
        
        return [(6, 0, booking.project_booking_anchor_ids.ids)]
    
    anchor_ids = fields.One2many('project.booking.anchor', 'feedback_id', string="Anchor", default=_default_anchor)
    testing_remarks = fields.Char('Testing Remarks', required="1")
    
    def add_feedback(self):
        anchor_list = []
        pr_book = self.env['project.booking'].browse(self._context.get('active_ids', []))
        for an in self.anchor_ids:
            anchor_list.append((0,0, {'anchor_type_id': an.anchor_type_id.id, 'anchor_size_id': an.anchor_size_id.id,
                                      'anchor_qty': an.anchor_qty, 'an_complexity': an.an_complexity, 'failer_qty': an.failer_qty, 'name': an.name}))
        
        if pr_book.booking_type in ['normal', 'special'] and pr_book and anchor_list:
            pr_book.feedback_anchor_ids = anchor_list
            pr_book.status = 'completed'
            pr_book.testing_remark = self.testing_remarks
        
        if pr_book and pr_book.booking_type in ['sic']:
            pr_book.status = 'completed'
            pr_book.testing_remark = self.testing_remarks
        return True
            
# class TestingReminder(models.TransientModel):
#     _name = 'testing.reminder'
#     
#     
#     def _get_partner(self):
#         if self._context.get('active_ids', False) and len(self._context.get('active_ids', False)) == 1:
#             pr_book = self.env['project.booking'].browse(self._context.get('active_ids'))
#             if pr_book and pr_book.partner_id and pr_book.partner_id.parent_id and pr_book.partner_id.parent_id.child_ids:
#                 return [('id', 'in', pr_book.partner_id.parent_id.child_ids.ids)]
#             else:
#                 return [('id', 'in', [])]
# 
#     partner_ids = fields.Many2many('res.partner', 'remider_id', 'partner_id', string="Stakeholders", domain=_get_partner)
#     
#     def tester_reminder(self):
#         if self._context.get('active_ids', False):
#             pr_book = self.env['project.booking'].browse(self._context.get('active_ids'))
#             total_reminder = self.env['ir.values'].get_default('admin.configuration', 'total_reminder')
#             reminder_duration = self.env['ir.values'].get_default('admin.configuration', 'reminder_duration')
#             send = False
#             if not pr_book.reminder_time:
#                 send = True
#             else:
#                 import datetime
#                 now = datetime.datetime.today()
#                 now = str(now).split('.')[0]
#                 diff = datetime.datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(pr_book.reminder_time, "%Y-%m-%d %H:%M:%S")
#                 total_hm = abs(diff)
#                 minutes = int(total_hm.total_seconds()/60)
#                 if minutes >= reminder_duration:
#                     send = True
#                 else:
#                     raise Warning(_("Reminder to stakeholders can be sent only after %s number of minutes.") % reminder_duration)
#                     send = False
#             if not total_reminder > pr_book.reminder_count:
#                 raise Warning(_("Reminder button to be clickable %s times.") % total_reminder)
#             if total_reminder > pr_book.reminder_count and send == True:
#                 import datetime
#                 pr_book.reminder_count = pr_book.reminder_count + 1
#                 for a in self.partner_ids:
#                     pr_book.reminder_time = datetime.datetime.now()
#                     ctx = dict(self._context or {})
#                     ctx['partner_email'] = a.id
#                     template = self.env.ref('hilti_modifier_customer_booking.email_template_for_reminder_id')
#                     template.with_context(ctx).send_mail(pr_book.id, force_send=True)
#                 pr_book.reminder_history = [(0,0,
#                                              {'reminder_count': pr_book.reminder_count,
#                                               'reminder_time': pr_book.reminder_time,
#                                               'partner_ids': [(6,0, self.partner_ids.ids)]})]
#                     
#         
#    