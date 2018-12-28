# -*- coding: utf-8 -*-
import datetime
import math
from dateutil import relativedelta
from odoo import api, fields, models, tools, _
from openerp.exceptions import ValidationError, Warning

class hr_employee(models.Model):
    _inherit = "hr.employee"

    boss_id = fields.Many2one('hr.employee', 'Boss')

    current_leave_state = fields.Selection(selection_add=[('cancel_request', 'Cancel Request')])

class HRHolidaysStatusBusinessTrip(models.Model):
    _inherit = 'hr.holidays.status'

    is_business_trip = fields.Boolean('Is Business Trip', help="Is leave type is Business Trip.")
    is_meeting = fields.Boolean('Is Meeting', help="Is Leave type is Meeting, Not allow to add leave on same Day.")
    max_back_date = fields.Integer(string='Max Back Date')

class HrHolidaysInherit(models.Model):
    _inherit = 'hr.holidays'

    @api.onchange('date_from', 'holiday_status_id', 'date_to')
    def _onchange_date_from(self):

        today_date = datetime.datetime.now()
        start_date = str(self.date_from)

        if str(self.date_from) != "False":
            date = datetime.datetime.strptime(start_date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if self.holiday_status_id:
                back_date = today_date - datetime.timedelta(days=self.holiday_status_id.max_back_date)
                if self.holiday_status_id.max_back_date > 0 :
                    if back_date.day > date.day:
                        raise Warning(
                            '%s Leave Type cannot be before %d days' % (
                            self.holiday_status_id.name, self.holiday_status_id.max_back_date))

        return super(HrHolidaysInherit, self)._onchange_date_from()


    attachment = fields.Binary('Document')
    file_name = fields.Char('File Name')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('cancel', 'Cancelled'),
        ('cancel_request', 'Cancel Request')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
            help="The status is set to 'To Submit', when a holiday request is created." +
            "\nThe status is 'To Approve', when holiday request is confirmed by user." +
            "\nThe status is 'Refused', when holiday request is refused by manager." +
            "\nThe status is 'Approved', when holiday request is approved by manager.")

    def get_notification_valeu(self, mail_id, employee_id, is_business_trip):
        return {
            'mail_id': mail_id,
            'emlpoyee_id': employee_id.id,
            'email_to': self.env['mail.mail'].browse(mail_id).email_to,
            'author_id' : self.env.user.id,
            'is_businnes_ref': is_business_trip,
        }

    @api.multi
    def action_cancel(self):
        return self.sudo().write({'state': 'cancel_request'})
    
    @api.multi
    def action_cancel_approve(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can Approve Cancel leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            holiday.write({'state': 'cancel', 'manager_id': manager.id})
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        return True
    
    @api.multi
    def action_approve(self):
        if self.type == 'remove':
            ctx  = {}
            email_list = []
            if self.holiday_status_id.is_business_trip:
                if not self.employee_id.boss_id or self.employee_id.boss_id.user_id != self.env.user:
                    raise Warning('You are Not allow to approve Business Trip type of leave, only Boss can Approve Business Trip leaves.')
            else:
                if not self.employee_id.leave_manager and self.employee_id.leave_manager.user_id != self.env.user or not self.department_id and self.department_id.manager_id and self.department_id.manager_id.user_id != self.env.user:
                    if not self.user_has_groups('hr_holidays.group_hr_holidays_manager'):
                        raise Warning('You are Not allow to approve leave, only Manager of Employee or HR manager can Approve it.')
            if self.employee_id.parent_id and self.employee_id.parent_id.user_id:
                email_list.append(self.employee_id.parent_id.user_id.email)
            if self.employee_id.leave_manager and self.employee_id.leave_manager.user_id:
                email_list.append(self.employee_id.leave_manager.user_id.email)
            if not email_list:
                email_list = [user.email for user in self.env['res.users'].search([]) if user.has_group('hr_holidays.group_hr_holidays_manager')]
            ctx['hr_account_email'] = ','.join([email for email in email_list if email])
            try:
                template = self.env.ref('modifier_teo_leave_management.employee_leave_request_approved_template', raise_if_not_found=False)
            except ValueError:
                pass
            if not template:
                template = self.env.ref('modifier_teo_leave_management.employee_leave_request_approved_template')
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            db = self.env.cr.dbname
            model = self.env.context.get('active_model')
            ctx['emp_name'] = self.employee_id.name
            ctx['action_url']  = "{}/web?db={}#id={}&view_type=form&model=hr.holidays".format(base_url, db, self.id)
            sent_mail = template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)
            if sent_mail:
                self.env['hr.holiday.notification'].create(self.get_notification_valeu(sent_mail, self.employee_id, self.holiday_status_id.is_business_trip))
        return super(HrHolidaysInherit, self).action_approve()

    def check_leave_apply_date(self, date_from):
        today_date = fields.date.today()
        date_from = date_from.split(" ")
        leave_date = datetime.datetime.strptime(str(date_from[0]), tools.DEFAULT_SERVER_DATE_FORMAT)
        if leave_date.date() >= today_date:
            raise Warning('You are Not allow apply meeting type of leave today. To apply Meeting Leave you have to apply for Leave in advance')
        return True

    @api.constrains('number_of_days_temp','holiday_status_id')
    def check_allocation_holidays(self):
        if self.type == 'remove' and self.holiday_status_id.pro_rate:
            date_today = datetime.datetime.today()
            default_allocation = self.holiday_status_id.default_leave_allocation
            join_date = datetime.datetime.strptime(str(self.employee_id.join_date), tools.DEFAULT_SERVER_DATE_FORMAT)
            after_one_year = join_date + relativedelta.relativedelta(years=1)
            after_three_month = join_date + relativedelta.relativedelta(months=3)
            if date_today < after_three_month:
                raise ValidationError(_('Sorry, You can not apply leave more than 0 Days!'))
            working_years = relativedelta.relativedelta(date_today, join_date).years
            pro_rate_month = relativedelta.relativedelta(date_today, join_date).months
            if working_years <= 0:
                number_of_days = math.ceil((float(pro_rate_month) /12) * 14)
            elif working_years >= 1 and working_years <= 5:
                number_of_days = 14.0
            elif working_years >= 6 and working_years <= 9:
                number_of_days = 15.0
            elif working_years >= 10 and working_years <= 13:
                number_of_days = 16.0
            elif working_years >= 14 and working_years <= 18:
                number_of_days = 17.0
            elif working_years >= 19:
                number_of_days = 18.0
            else:
                number_of_days = 0.0
            if self.number_of_days_temp > number_of_days:
                raise ValidationError(_('Sorry, You can not apply leave more than %s Days!' % (number_of_days)))

    @api.model
    def create(self, values):
        if self.env["hr.holidays.status"].browse([values.get('holiday_status_id')]).is_meeting:
            check_date = self.check_leave_apply_date(values.get('date_from'))
        res = super(HrHolidaysInherit, self).create(values)
        if res.type == 'remove':
            ctx  = {}
            if res.holiday_status_id.is_business_trip:
                if res.employee_id.boss_id and res.employee_id.boss_id.user_id:
                    ctx['boss_users'] =  res.employee_id and res.employee_id.boss_id.user_id.email
                else:
                    raise Warning('No Boss Define in Employee, To add Business Trip type leave need Boss in Employee. Please Contact HR Manager/ Admin.')
            else:
                email_list = []
                if res.department_id and res.department_id.manager_id:
                    email_list.append(res.department_id.manager_id.user_id.email)
                if res.employee_id.leave_manager and res.employee_id.leave_manager.user_id:
                    email_list.append(res.employee_id.leave_manager.user_id.email)
                if not email_list:
                    email_list = [user.email for user in self.env['res.users'].search([]) if user.has_group('hr_holidays.group_hr_holidays_manager')]
                ctx['hr_manager_email'] = ','.join([email for email in email_list])
            try:
                template = self.env.ref('modifier_teo_leave_management.employee_leave_request_template', raise_if_not_found=False)
            except ValueError:
                pass
            if not template:
                template = self.env.ref('modifier_teo_leave_management.employee_leave_request_template')
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            db = self.env.cr.dbname
            model = self.env.context.get('active_model')
            ctx['emp_name'] = res.employee_id.name
            ctx['action_url']  = "{}/web?db={}#id={}&view_type=form&model=hr.holidays".format(base_url, db, res.id)
            sent_mail = template.with_context(ctx).send_mail(res.id, force_send=True, raise_exception=False)
            if sent_mail:
                self.env['hr.holiday.notification'].create(self.get_notification_valeu(sent_mail, res.employee_id, res.holiday_status_id.is_business_trip))
        return res

    @api.multi
    def write(self, values):
        if 'holiday_status_id' or 'date_from' in values:
            if self.holiday_status_id.is_meeting:
                from_date = self.date_from
                if 'date_from' in values:
                    from_date = values['date_from']
                check_date = self.check_leave_apply_date(from_date)
        return super(HrHolidaysInherit, self).write(values)

