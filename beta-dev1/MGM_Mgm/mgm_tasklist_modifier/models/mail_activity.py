# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta

from odoo import api, exceptions, fields, models, _, modules, SUPERUSER_ID

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        default=lambda self: self.env.user,
        index=True, required=True)
    department_id = fields.Many2one('hr.department', string="Department")
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_mail_activity_rel', 'employee_id', 'activity_id', 'Employees')

    @api.onchange('department_id')
    def onchange_department_id(self):
        self.employee_ids = self.env['hr.employee'].search([('department_id', '=', self.department_id.id),('department_id', '!=', False)])

    @api.model
    def create(self, values):
        # already compute default values to be sure those are computed using the current user
        values_w_defaults = self.default_get(self._fields.keys())
        values_w_defaults.update(values)
        # continue as sudo because activities are somewhat protected

        activity = super(MailActivity, self.sudo()).create(values_w_defaults)

        if values.get('employee_ids', False):
            action_id = self.env.ref("task_list_manager.mail_activity_action")
            view = 'To Do List'
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            link = base_url + '/web#view_type=kanban&model=mail.activity&action=%s' % action_id.id
            email_from = self.env.user.company_id.email or 'Administrator <admin@example.com>'
            subject = ' You have New Activity in your To Do List..!! '

            for employee in activity.employee_ids:
                if employee.user_id:
                    if employee.user_id != activity.user_id:
                        vals = {'activity_category': activity.activity_category,
                                'activity_type_id': activity.activity_type_id.id,
                                'date_deadline': activity.date_deadline,
                                'department_id': activity.department_id.id,
                                'note': activity.note,
                                'previous_activity_type_id': activity.previous_activity_type_id.id,
                                'recommended_activity_type_id': activity.recommended_activity_type_id.id,
                                'res_id': activity.res_id,
                                'res_model': activity.res_model,
                                'res_model_id': activity.res_model_id.id,
                                'summary': activity.summary,
                                'user_id': employee.user_id.id}

                        self.create(vals)

                    """ send email """
                    email_to = employee.user_id.login
                    message = """
                        <p>
                            Dear %s,
                        </p>

                        <p>
                            You have New Activity in your To Do List. 
                        </p>

                        <div>
                        <a href=%s style = "padding: 5px 10px; font-size: 12px; line-height: 18px;
                         color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block;
                         margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle;
                         cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B;
                         border: 1px solid #875A7B; border-radius:3px">View %s</a>
                         </div>

                        <p> Thank You. </p>      
                        """ % (employee.name, link, view)

                    vals = {
                        'state': 'outgoing',
                        'subject': subject,
                        'body_html': '%s' % message,
                        'email_to': email_to,
                        'email_from': email_from,
                    }

                    if vals:
                        email_id = self.env['mail.mail'].create(vals)
                        if email_id:
                            email_id.send()

        activity_user = activity.sudo(self.env.user)
        activity_user._check_access('create')
        try:
            self.env[activity_user.res_model].browse(activity_user.res_id).message_subscribe(partner_ids=[activity_user.user_id.partner_id.id])
        except exceptions.AttributeError:
            pass
        if activity.date_deadline <= fields.Date.today():
            self.env['bus.bus'].sendone(
                (self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
                {'type': 'activity_updated', 'activity_created': True})
        return activity_user

