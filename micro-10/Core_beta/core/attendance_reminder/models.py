# -*- coding: utf-8 -*-

from datetime import datetime, date
from openerp import SUPERUSER_ID
from openerp import api, fields, models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _cron_attendance_reminder(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        current_date = datetime.now()
        for employee in self.env['hr.employee'].search([]):
            if employee:
                try:
                    employee.contract_ids
                    if employee.contract_ids[
                        0].working_hours.attendance_ids.search([
                        ('dayofweek', '=', date.today().weekday())
                    ]):
                        print "333333333333", current_date, type(current_date)
                        emp_attendance = self.env['hr.attendance'].search_count(
                                [
                                    ('employee_id', '=', employee.id),
                                    ('check_in', '>=', current_date.strftime('%Y-%m-%d 00:00:00')),
                                    ('check_out', '<=', current_date.strftime('%Y-%m-%d 23:59:59')),
                                ])
                        print "Fffffffffffffff", emp_attendance
                        if emp_attendance < 1:
                            emp_holiday = self.env['hr.holidays'].search_count([
                                ('employee_id', '=', employee.id),
                                ('employee_id', '!=',
                                 employee.department_id.manager_id.id),
                                ('date_from', '<=',
                                 current_date.strftime('%Y-%m-%d 00:00:00')),
                                ('date_to', '>=',
                                 current_date.strftime('%Y-%m-%d 00:00:00')),
                            ])
                            if emp_holiday < 1:
                                template_id = \
                                self.env['ir.model.data'].get_object_reference(
                                        'attendance_reminder',
                                        'email_template_edi_attendance_reminder')[
                                    1]
                                email_template_obj = self.env[
                                    'mail.template'].browse(template_id)
                                if template_id:
                                    values = email_template_obj.generate_email(
                                        template_id, employee.id)
                                    values['email_from'] = su_id.email
                                    values['email_to'] = employee.work_email
                                    values['res_id'] = False
                                    mail_mail_obj = self.env['mail.mail']
                                    msg_id = mail_mail_obj.create(values)
                                    if msg_id:
                                        mail_mail_obj.send([msg_id])
                except Exception as e:
                    print "DDDDDDDDDDDDDD", e
                    continue
