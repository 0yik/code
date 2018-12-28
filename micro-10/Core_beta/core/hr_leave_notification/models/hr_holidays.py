from datetime import datetime, timedelta

from odoo import api, fields, models, tools, _

class HrHolidays(models.Model):

    _inherit = "hr.holidays"

    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        holiday = super(HrHolidays, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(values)
        if holiday.employee_id and holiday.employee_id.leave_manager:
            temp_id = self.env['ir.model.data'].get_object_reference('hr_leave_notification', 'hm_email_temp_hr_holiday_hm')[1]
            res = self.send_email(holiday.id, temp_id, force_send=True)
        return holiday

    @api.multi
    def from_mail(self):
        mail_server_ids = self.env['ir.mail_server'].search([],order="id desc", limit=1)
        if not mail_server_ids:
            raise Warning(_('Mail Error \n No mail outgoing mail server specified!'))
        if mail_server_ids.ids:
            return mail_server_ids.smtp_user or ''

    @api.multi
    def get_manager_work_email(self):
        for holiday in self:
            mail = ''
            if holiday.employee_id.leave_manager:
                mail = holiday.employee_id.leave_manager.work_email
            return mail
    
    @api.multi
    def get_system_url(self):
        url = self.env['ir.config_parameter'].search([('key','=','web.base.url')], limit=1)
        if url:
            return url.value
        return ''