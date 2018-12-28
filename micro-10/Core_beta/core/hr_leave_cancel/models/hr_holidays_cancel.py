# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import timedelta
from openerp.tools import float_compare
import math

HOURS_PER_DAY = 8

class Holidays(models.Model):

    _name = "hr.holidays.cancel"
    _description = "Leave Cancellation"
    # _order = "type desc, date_from desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char('Description', required=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a holiday cancel request is created." +
             "\nThe status is 'To Approve', when holiday cancel request is confirmed by user." +
             "\nThe status is 'Refused', when holiday request cancel is refused by manager." +
             "\nThe status is 'Approved', when holiday request cancel is approved by manager.")
    report_note = fields.Text('HR Comments')
    holiday = fields.Many2one("hr.holidays", string="Leaves", required=True, )
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=_default_employee)
    date_from = fields.Datetime('Start Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)]})
    date_to = fields.Datetime('End Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)]})
    number_of_days = fields.Float('Number of Days', compute='_compute_number_of_days', store=True)
    type = fields.Selection([
            ('remove', 'Leave Request'),
            ('add', 'Allocation Request')
        ], string='Request Type', required=True, readonly=True, index=True, default='remove',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Choose 'Leave Request' if someone wants to take an off-day. "
             "\nChoose 'Allocation Request' if you want to increase the number of leaves available for someone")
    number_of_days_temp = fields.Float('Allocation', readonly=True, copy=False,
        states={'draft': [('readonly', False)]})

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for obj in self:
            if obj.date_from < obj.holiday.date_from:
                raise ValidationError(_('Please select the duration date between %s and %s.' % (fields.Datetime.from_string(obj.holiday.date_from).strftime('%d/%m/%Y %H:%M'),fields.Datetime.from_string(obj.holiday.date_to).strftime('%d/%m/%Y %H:%M') )))
            if obj.date_to > obj.holiday.date_to:
                raise ValidationError(_('Please select the duration date between %s and %s.' % (fields.Datetime.from_string(obj.holiday.date_from).strftime('%d/%m/%Y %H:%M'),fields.Datetime.from_string(obj.holiday.date_to).strftime('%d/%m/%Y %H:%M') )))

    @api.constrains('number_of_days_temp')
    def _check_difference_of_date(self):
        for obj in self:
            from_dt = fields.Datetime.from_string(obj.date_from)
            to_dt = fields.Datetime.from_string(obj.date_to)
            time_delta = to_dt - from_dt
            new_day = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
            if new_day != obj.number_of_days_temp:
                raise ValidationError(_("You can not modify value of days."))

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        for obj in self:
            if obj.date_from > obj.date_to:
                raise ValidationError(_("Warning! \n The start date must be anterior to the end date."))       

    @api.multi
    @api.depends('number_of_days_temp', 'type')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.type == 'remove':
                holiday.number_of_days = -holiday.number_of_days_temp
            else:
                holiday.number_of_days = holiday.number_of_days_temp

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            resource = employee.resource_id.sudo()
            if resource and resource.calendar_id:
                hours = resource.calendar_id.get_working_hours(from_dt, to_dt, resource_id=resource.id, compute_leaves=True)
                uom_hour = resource.calendar_id.uom_id
                uom_day = self.env.ref('product.product_uom_day')
                if uom_hour and uom_day:
                    return uom_hour._compute_quantity(hours, uom_day)

        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

    @api.onchange('holiday')
    def _onchange_holiday(self):
        if self.holiday:
            self.date_from = self.holiday.date_from
            self.date_to = self.holiday.date_to
        else:
            self.date_from = False
            self.date_to = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.date_from = False
            self.date_to = False
            self.holiday = False
        else:
            self.date_from = False
            self.date_to = False
            self.holiday = False
        
    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0
            
    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0                          

    @api.multi
    def action_approve(self):
        # Commenting old code to enhance functionality for partial cancel leave
        #for record in self:
        #    record.holiday.action_refuse()
        #    record.write({'state': 'validate'})
        #new code for partially cance leave
        for record in self:
            from_dt_full = fields.Datetime.from_string(record.date_from)
            to_dt_full = fields.Datetime.from_string(record.date_to)
            # approved leave for holiday
            app_from_dt_full = fields.Datetime.from_string(record.holiday.date_from)
            app_to_dt_full = fields.Datetime.from_string(record.holiday.date_to)
            
            # only date
            from_dt = fields.Datetime.from_string(record.date_from).strftime('%Y-%m-%d')
            to_dt = fields.Datetime.from_string(record.date_to).strftime('%Y-%m-%d')
            # approved leave for holiday
            app_from_dt = fields.Datetime.from_string(record.holiday.date_from).strftime('%Y-%m-%d')
            app_to_dt= fields.Datetime.from_string(record.holiday.date_to).strftime('%Y-%m-%d')
            
            if fields.Date.from_string(app_from_dt) == fields.Date.from_string(from_dt) and fields.Date.from_string(app_to_dt) == fields.Date.from_string(to_dt):
                record.holiday.action_refuse()
                record.write({'state': 'validate'})
            # condition for the first date
            elif fields.Date.from_string(app_from_dt) ==  fields.Date.from_string(from_dt) and fields.Date.from_string(to_dt) < fields.Date.from_string(app_to_dt):
                record.holiday.write({'date_from': fields.Datetime.to_string(from_dt_full + timedelta(days=record.number_of_days_temp))})
                record.holiday._onchange_date_from()
                record.write({'state': 'validate'})
            elif fields.Date.from_string(app_to_dt) ==  fields.Date.from_string(to_dt) and fields.Date.from_string(from_dt) > fields.Date.from_string(app_from_dt):
                record.holiday.write({'date_to': fields.Datetime.to_string(to_dt_full - timedelta(days=record.number_of_days_temp))})
                record.holiday._onchange_date_to()
                record.write({'state': 'validate'})
            else:
                raise UserError(_("You can not cancel between date leave."))
                
    @api.model
    def create(self, vals):
        res = super(Holidays, self).create(vals)
        res._onchange_date_from()
        res._onchange_date_to()
        return res
    @api.multi
    def action_refuse(self):
        for record in self:
            record.write({'state': 'refuse'})

    @api.multi
    def action_confirm(self):
        """
        Confirm leave cancel requests and send a mail to the concerning department head.
        :return:
        """
        for record in self:
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.work_email:
                vals = {
                        'email_to': record.employee_id.parent_id.work_email,
                        'subject': 'Leave Cancel Request: From {employee} , {description}'
                                    .format(employee=record.employee_id.name, description=record.name),
                        'body_html': """
                                    <p>
                                        Hello Mr {manager},
                                    </p>
                                    <p>
                                        There is a leave cancellation request on an approved leave {leave}
                                    </p>
                                    <p>
                                        Thank You.
                                    </p>
                                """.format(manager=record.employee_id.parent_id.name, leave=record.holiday.display_name)}
                mail = self.env['mail.mail'].sudo().create(vals)
                mail.send()
            record.write({'state': 'confirm'})
