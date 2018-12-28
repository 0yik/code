# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta, time, date
import pytz
# import time
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.exceptions import except_orm, Warning
from dateutil import tz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT

class admin_configuration(models.TransientModel):

    _inherit = 'admin.configuration'

    request_half_day_hours = fields.Integer('Unavailability request-Half day criteria', default=4)

    @api.multi
    def set_request_half_day_hours_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'admin.configuration', 'request_half_day_hours', self.request_half_day_hours)

class project_booking(models.Model):

    _inherit = 'project.booking'

    @api.model
    def retrieve_booking_dashboard(self):
        res = super(project_booking, self).retrieve_booking_dashboard()
        my_request = self.env['my.request']
        x_days_after_datetime = datetime.strftime(datetime.combine((datetime.now() + timedelta(days=7)), time.max), DEFAULT_SERVER_DATETIME_FORMAT)
        day_start = datetime.strftime(datetime.combine((datetime.now()), time.min), DEFAULT_SERVER_DATETIME_FORMAT)
        day_end = datetime.strftime(datetime.combine((datetime.now()), time.max), DEFAULT_SERVER_DATETIME_FORMAT)
        today_request = len(my_request.search([('req_type', '=', 'unavailability'), ('full_start_date', '>=', day_start), ('full_start_date', '<=', day_end)]).ids)
        x_days_request = len(my_request.search([('req_type', '=', 'unavailability'), ('full_start_date', '<=', x_days_after_datetime), ('full_start_date', '>=', day_start)]).ids)
        res.update({
            'requests': {
                'today': today_request,
                'next_7_days': x_days_request,
            }
        })
        return res

class ot_request(models.Model):
    _name = 'ot.request'

    ot_start_date = fields.Datetime('Start Date & Time', required=True)
    ot_end_date = fields.Datetime('End Date & Time', required=True)
    duration = fields.Float('Duration')
    t_re_id = fields.Many2one('my.request')
#     duration_compute = fields.Char('Duration', compute='_compute_duration_req')

    def validate_date(self, start_date, end_date):
        ot_start_date = datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        ot_end_date = datetime.strptime(end_date, DEFAULT_SERVER_DATETIME_FORMAT)
        if ot_start_date > ot_end_date:
            raise UserError(_('End date should be greater then Start date.'))
        if ot_start_date < datetime.now():
            raise UserError(_('You can not enter past date.'))
        if ot_end_date < datetime.now():
            raise UserError(_('You can not enter past date.'))
        return True

    def calculate_overtime(self, ot_start_date, ot_end_date):
        is_holiday = False
        start_date = datetime.strftime(datetime.strptime(ot_start_date, DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
        end_date = datetime.strftime(datetime.strptime(ot_end_date, DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
        start_date_day_name = datetime.strftime(datetime.strptime(ot_start_date, DEFAULT_SERVER_DATETIME_FORMAT), '%A')
        end_date_day_name = datetime.strftime(datetime.strptime(ot_end_date, DEFAULT_SERVER_DATETIME_FORMAT), '%A')
        if start_date_day_name in ["Sunday", "Saturday"] and end_date_day_name in ["Sunday", "Saturday"]:
            diff = datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT) 
            if ((diff.total_seconds() / 60) / 60) <= 48:
                is_holiday = True
        if not is_holiday:
            holidays = self.env['holiday.holiday'].search(['|', ('holiday_date', '=', start_date), ('holiday_date', '=', end_date)])
            if holidays:
                is_holiday = True
        if not is_holiday:
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz(self.env.user.tz)
            start_time = (datetime.strptime(ot_start_date, DEFAULT_SERVER_DATETIME_FORMAT).replace(tzinfo=from_zone)).astimezone(to_zone).replace(tzinfo=None)
            end_time = (datetime.strptime(ot_end_date, DEFAULT_SERVER_DATETIME_FORMAT).replace(tzinfo=from_zone)).astimezone(to_zone).replace(tzinfo=None)
            ot_start_time = self.env['ir.values'].get_default('admin.configuration', 'ot_start_time')
            ot_end_time = self.env['ir.values'].get_default('admin.configuration', 'ot_end_time')
            if ot_start_time and ot_end_time:
                conf_start_time = ot_start_time
                conf_end_time = ot_end_time
                start = datetime.combine(datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(conf_start_time), (conf_start_time * 60) % 60, (conf_start_time * 3600) % 60), "%H:%M:%S").time())
                end = datetime.combine(datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(conf_end_time), (conf_end_time * 60) % 60, (conf_end_time * 3600) % 60), "%H:%M:%S").time())
                if conf_start_time > conf_end_time:
                    end = end + timedelta(days=1)
                if (start <= start_time <= end) and  (start <= end_time <= end):
                    return True
                else:
                    if end_date_day_name not in ["Sunday", "Saturday"] or start_date_day_name != 'Friday':
                        raise UserError(_('Selected start time ' + datetime.strftime(start_time, DEFAULT_SERVER_DATETIME_FORMAT) +' or end time ' + datetime.strftime(end_time, DEFAULT_SERVER_DATETIME_FORMAT) + ' are not in overtime.'))
            else:
                raise UserError(_('Please contact your admin for the  configuration of overtime working hours.'))
        return True

    @api.onchange('ot_start_date', 'ot_end_date')
    @api.depends('ot_start_date', 'ot_end_date')
    def onchange_datetime(self):
        if 'req_type' in self._context and self._context.get('req_type') == 'overtime':
            if self.ot_start_date and self.ot_end_date:
                duration = abs(datetime.strptime(self.ot_end_date, "%Y-%m-%d %H:%M:%S") - datetime.strptime(self.ot_start_date, "%Y-%m-%d %H:%M:%S"))
                self.duration = abs((duration.total_seconds() / 60) / 60)
                print 'ggggggggggggggggg', self.duration

    @api.model
    def create(self, vals):
        self.validate_date(vals.get('ot_start_date'), vals.get('ot_end_date'))
        if vals.get('ot_start_date') and vals.get('ot_end_date'):
            not_overtime = self.calculate_overtime(vals.get('ot_start_date'), vals.get('ot_end_date'))
            duration = abs(datetime.strptime(vals.get('ot_end_date'), "%Y-%m-%d %H:%M:%S") - datetime.strptime(vals.get('ot_start_date'), "%Y-%m-%d %H:%M:%S"))
            vals['duration'] = (duration.total_seconds() / 60) / 60
        return super(ot_request, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(ot_request, self).write(vals)
        for rec in self:
            if vals.get('ot_start_date') or vals.get('ot_end_date'):
                start_date = vals.get('ot_start_date') or rec.ot_start_date
                end_date = vals.get('ot_end_date') or rec.ot_end_date
                self.validate_date(start_date, end_date)
                not_overtime = self.calculate_overtime(start_date, end_date)
                duration = abs(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S") - datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
                rec.duration = (duration.total_seconds() / 60) / 60
        return res

class tester_myreqest(models.Model):
    _name = 'my.request'
    _rec_name = 'req_no'
    _order = 'id DESC'


    @api.model
    def get_overtime_config_time(self):
        vals = {}
        vals["ot_start_time"] = self.env['ir.values'].get_default('admin.configuration', 'ot_start_time')
        vals["ot_end_time"] = self.env['ir.values'].get_default('admin.configuration', 'ot_end_time')
        return vals

    @api.model
    def _default_overtime_start_time(self):
        return self.env['ir.values'].get_default('admin.configuration', 'ot_start_time')

    @api.model
    def _default_overtime_end_time(self):
        return self.env['ir.values'].get_default('admin.configuration', 'ot_end_time')

    req_no = fields.Char('Req No.')
    user_id = fields.Many2one('res.users', string="Tester")
    partner_id = fields.Many2one('res.partner', related="user_id.partner_id", string="Tester")
    req_type = fields.Selection([('unavailability', 'Unavailability'), ('overtime', 'Overtime')], required=True, default='unavailability')
    description = fields.Text('Description')
    start_date = fields.Datetime('Start Date &;amp Time')
    end_date = fields.Datetime('End Date &;amp Time', compute='half_day_hours')
    half_day_hour = fields.Float('Hours')
    full_start_date = fields.Date('Start Date')
    full_end_date = fields.Date('End Date')
    is_half_leave = fields.Boolean("Half day", default=True)
    days_compute = fields.Float('Duration', compute='onchange_full_date')
    duration_compute = fields.Float('Total Duration', compute='half_day_hours')
    status = fields.Selection([('draft', 'Draft'),
                               ('awaitinapprovel', 'Awaiting Approval'),
                               ('approved', 'Approved'),
                               ('reject', 'Reject'),
                               ('cancel', 'Cancel'), ],
                              string='Status', default='draft', copy=False)
    ot_req_ids = fields.One2many('ot.request', 't_re_id', string="Overtime Request")

    overtime_start_time = fields.Float('Overtime Start Time', default=_default_overtime_start_time)
    overtime_end_time = fields.Float('Overtime End Time', default=_default_overtime_end_time)

    @api.one
    @api.constrains('half_day_hour')
    def _check_half_day_hour(self):
        config_hours = self.env['ir.values'].get_default('admin.configuration', 'request_half_day_hours')
        if self.half_day_hour and self.half_day_hour > config_hours:
            raise UserError(_('The hours requested for half day-unavailability must be within ' + str(config_hours) + ' hours.\nPlease apply for the full day request if you wish to request for more no. of hours. Thank you.'))

    @api.one
    @api.depends('half_day_hour', 'start_date', 'ot_req_ids', 'ot_req_ids.duration', 'req_type')
    def half_day_hours(self):
        if self.start_date and self.half_day_hour and self.is_half_leave == True:
            self.end_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=self.half_day_hour)
            self.duration_compute = self.half_day_hour
        if self.req_type == 'overtime' and self.ot_req_ids:
            total_duration = 0.00
            for ot_req_ids in self.ot_req_ids:
                total_duration += ot_req_ids.duration
                print 'dddddddddddddddddddd', ot_req_ids.duration
            self.duration_compute = total_duration

    def validate_date(self):
        
        for rec in self:
            if rec.start_date and rec.end_date:
                
                start_date = datetime.strptime(rec.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end_date = datetime.strptime(rec.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                
                if start_date > end_date:
                    raise UserError(_('Please check your start and end dates for request. Start dates must be lower than end dates.'))
                
                if start_date < datetime.now():
                    raise UserError(_('You can not enter past date.'))
                
            if rec.full_start_date and rec.full_end_date:
                
                full_start_date = datetime.strptime(rec.full_start_date, DEFAULT_SERVER_DATE_FORMAT)
                full_end_date = datetime.strptime(rec.full_end_date, DEFAULT_SERVER_DATE_FORMAT)
                
                if full_start_date > full_end_date:
                    raise UserError(_('Please check your start and end dates for request. Start dates must be lower than end dates.'))
                
                if full_start_date < datetime.now():
                    raise UserError(_('You can not enter past date.'))
                
                if full_end_date < datetime.now():
                    raise UserError(_('You can not enter past date.'))
                
        return True

    @api.model
    def create(self, vals):
        if vals.get('req_type') == 'overtime' and not vals.get('ot_req_ids'):
            raise UserError(_('Please select time.'))
        vals['req_no'] = self.env['ir.sequence'].next_by_code('my.request') or _('New')
        if not vals.get('user_id'):
            vals.update({
                'user_id': self.env.user.id,
            })
        if vals.get('start_date') and vals.get('half_day_hour') and vals.get('is_half_leave') and not vals.get('end_date'):
            vals['end_date'] = datetime.strftime(datetime.strptime(vals.get('start_date'), DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=vals.get('half_day_hour')), DEFAULT_SERVER_DATETIME_FORMAT)
            vals['duration_compute'] = vals.get('half_day_hour')
        result = super(tester_myreqest, self).create(vals)
        result.validate_date()
#         if result.full_start_date and result.full_end_date and result.is_half_leave == False:
#             date_format = "%Y-%m-%d"
#             a = datetime.strptime(result.full_start_date, date_format)
#             b = datetime.strptime(result.full_end_date, date_format)
#             delta = b - a
#             result.days_compute = int(delta.days) + 1
        if result and result.req_type == 'overtime' and result.ot_req_ids:
            total_duration = 0.00
            for ot_req_ids in result.ot_req_ids:
                total_duration += ot_req_ids.duration
            result.duration_compute = total_duration
        return result

    @api.multi
    def write(self, vals):
        for self_obj in self:
            if self_obj.req_type == 'overtime' and 'ot_req_ids' in vals and self_obj.status == 'approved':
                for line in vals['ot_req_ids']:
                    if line[0] in [1, 2]:
                        booking_ids = self._get_booking_list(self_obj)
                        booking_name = ''
                        for book_obj in booking_ids:
                            if not booking_name:
                                booking_name = book_obj.booking_no
                            else:
                                booking_name += ',' + book_obj.booking_no
                        if booking_name:
                            raise ValidationError(
                                # _('You are already booked for the below listed Customer Booking:\
                                #  \n %s \n Please contact your Administrator.' % (booking_name)
                                _('This overtime request cannot be modified as you are already booked for the Booking %s. Please contact your admin for further assistance on modification.' % (booking_name)))
                    else:
                        continue
        res = super(tester_myreqest, self).write(vals)
        for rec in self:
            if (('req_type' in vals and vals.get('req_type') == 'unavailability') and ('is_half_leave' in vals and not vals.get('is_half_leave'))) or ('full_start_date' in vals and vals.get('full_start_date')) or ('full_end_date' in vals and vals.get('full_end_date')):
#                 date_format = "%Y-%m-%d"
#                 a = datetime.strptime(vals.get('full_start_date') or rec.full_start_date, date_format)
#                 b = datetime.strptime(vals.get('full_end_date') or rec.full_end_date, date_format)
#                 delta = b - a
#                 rec.days_compute = int(delta.days) + 1
                rec.end_date = False
                rec.start_date = False
                rec.half_day_hour = 0.00
                rec.duration_compute = 0.00
                rec.ot_req_ids.unlink()
            if (('req_type' in vals and vals.get('req_type') == 'unavailability') and ('is_half_leave' in vals and vals.get('is_half_leave'))) or ('start_date' in vals and vals.get('start_date')) or ('half_day_hour' in vals and vals.get('half_day_hour')):
                rec.end_date = datetime.strptime(vals.get('start_date') or rec.start_date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=vals.get('half_day_hour') or rec.half_day_hour)
#                 rec.duration_compute = rec.half_day_hour
                rec.full_start_date = False
                rec.full_end_date = False
                rec.days_compute = 0.00
                rec.ot_req_ids.unlink()
            if 'ot_req_ids' in vals and vals.get('req_type') == 'overtime':
#                 total_duration = 0.00
#                 for time in rec.ot_req_ids:
#                     total_duration += float(time.duration)
#                 rec.duration_compute = abs(total_duration)
                rec.full_start_date = False
                rec.full_end_date = False
                rec.start_date = False
                rec.end_date = False
                rec.days_compute = 0.00
                rec.half_day_hour = 0.00
                rec.duration_compute = 0.00
        self.validate_date()
        return res

    @api.multi
    def waiting_approvel(self):
        for rec in self:
            if rec.req_type == 'overtime':
                rec.status = 'approved'
            else:
                rec.status = 'awaitinapprovel'
        return True

    def _get_booking_list(self, req_obj):
        # Reusable function to find booking list for particular tester
        booking_ids = []
        if req_obj.req_type == 'overtime':
            for line in req_obj.ot_req_ids:
                booking_tester_id = self.env['project.booking'].sudo().search(
                    [('tester_id', '=', req_obj.user_id.partner_id.id),
                     ('status', 'not in', ['completed', 'cancelled']),
                     ('final_start_dtime', '>=', line.ot_start_date),
                     ('final_end_dtime', '<=', line.ot_end_date),
                     ])
                for booking in booking_tester_id:
                    booking_ids.append(booking)
        else:
            # unavailibility
            if req_obj.is_half_leave:
                print "stuff for half leave"
                # adding total hours into the start date so that we get
                # exact end time of the leave (unavailibitity)
                end_time = fields.Datetime.from_string(
                    req_obj.start_date) + timedelta(minutes=int(req_obj.half_day_hour * 60))
                booking_tester_id = self.env['project.booking'].sudo().search(
                    [('tester_id', '=', req_obj.user_id.partner_id.id),
                     ('status', 'not in', ['completed', 'cancelled']),
                     ('final_start_dtime', '>=', req_obj.start_date),
                     ('final_end_dtime', '<=', fields.Datetime.to_string(end_time)),
                     ])
                for booking in booking_tester_id:
                    booking_ids.append(booking)
            else:
                # Stuff for full day
                booking_tester_id = self.env['project.booking'].sudo().search(
                    [('tester_id', '=', req_obj.user_id.partner_id.id),
                     ('status', 'not in', ['completed', 'cancelled']),
                     ('final_start_dtime', '>=', req_obj.full_start_date),
                     ('final_end_dtime', '<=', req_obj.full_end_date),
                     ])
                for booking in booking_tester_id:
                    booking_ids.append(booking)
        return booking_ids

    def send_notification_cancel(self, req_obj):
        # TODO send notification function for Mustafa
        return True

    @api.multi
    def action_cancel(self):
        for req_obj in self:
            if req_obj.req_type == 'unavailability':
                # NOT half leave
                if not req_obj.is_half_leave:
                    if req_obj.full_start_date >= fields.Date.today():

                        # #TODO send notification
                        self.send_notification_cancel(req_obj)
                        req_obj.status = 'cancel'
                    elif req_obj.full_start_date <= fields.Date.today() and (self._uid == 1 or self.env.user.has_group('hilti_modifier_accessrights.group_hilti_admin')):
                        req_obj.status = 'cancel'
                    else:
                        raise ValidationError(_("The Unavailability or OT requests for the past days cannot be cancelled."))
                else:
                    # # HALF LEAVE
                    if req_obj.start_date >= fields.Datetime.now():
                        # #TODO send notification
                        self.send_notification_cancel(req_obj)
                        req_obj.status = 'cancel'
                    elif req_obj.start_date <= fields.Datetime.now() and (self._uid == 1 or self.env.user.has_group('hilti_modifier_accessrights.group_hilti_admin')):
                        req_obj.status = 'cancel'
                    else:
                        raise ValidationError(_("The Unavailability or OT requests for the past days cannot be cancelled."))
                return True
            # # for OVERTIME
            else:
                for ot_line in req_obj.ot_req_ids:
                    if fields.Datetime.now() <= ot_line.ot_start_date:
                        req_obj.status = 'cancel'
                    elif ot_line.ot_start_date <= fields.Datetime.now() and (self._uid == 1 or self.env.user.has_group('hilti_modifier_accessrights.group_hilti_admin')):
                        req_obj.status = 'cancel'
                    else:
                        raise ValidationError(_("The Unavailability or OT requests for the past days cannot be cancelled."))
                # # first we check that if tester is booked for that overtime
                booking_ids = self._get_booking_list(req_obj)
                booking_name = ''
                for book_obj in booking_ids:
                    if not booking_name:
                        booking_name = book_obj.booking_no
                    else:
                        booking_name += ',' + book_obj.booking_no
                if booking_name:
                    raise ValidationError(
                        # _('You are already booked for the below listed Customer Booking:\
                        #  \n %s \n Please contact your Administrator.' % (booking_name)
                        _('You cannot cancel this overtime request as you \
                          are already booked for the Booking %s. Please \
                          contact your admin if you still wish to cancel it.' % (booking_name)))
                if not booking_ids:
                    # TODO SEND NOTIFICATION TO ADMIN
                    self.send_notification_cancel(req_obj)
                    req_obj.status = 'cancel'
                return True

    def state_approvel(self):
        if self.req_type == 'unavailability':
            local = pytz.timezone(self._context.get('tz'))
            if self.user_id and self.user_id.partner_id:
                booking_tester_ids = self.env['project.booking'].search([('tester_id', '=', self.user_id.partner_id.id)])
                total_booking_affect = []
                if not self.is_half_leave:
                    for a in booking_tester_ids:
                        check_dt_start = datetime.strptime(a.final_start_dtime, "%Y-%m-%d %H:%M:%S")
                        start_date = pytz.utc.localize(check_dt_start, is_dst=None).astimezone(local).date()
                        check_dt_end = datetime.strptime(a.final_end_dtime, "%Y-%m-%d %H:%M:%S")
                        end_date = pytz.utc.localize(check_dt_end, is_dst=None).astimezone(local).date()
                        if self.full_start_date in [str(start_date), str(end_date)] or self.full_end_date in [str(start_date), str(end_date)]:
                            total_booking_affect.append(str(a.booking_no))
                if self.is_half_leave:
                    # commented code developed by nitin
                    # for b in booking_tester_ids:
                    #    if (b.final_start_dtime <= self.start_date <= b.final_end_dtime) or (b.final_start_dtime <= self.end_date <= b.final_end_dtime):
                    #        total_booking_affect.append(str(b.booking_no))
                    # Added custom search code for the booking search
                    booking_ids = self._get_booking_list(self)
                    for booking_obj in booking_ids:
                        total_booking_affect.append(str(booking_obj.booking_no))
                if total_booking_affect:
                    str1 = ','.join(str(e) for e in total_booking_affect)
                    # raise Warning(_("First you have to Re-assign tester for %s bookings then you can able approve Unavailability.") % str1)
                    raise Warning(_("The Tester has already been booked for the booking(s) -  %s.\n \
                                    To approve the Unavailability Request for this tester, \
                                    please use Re-assign Tester fuctionality from bookings and then approve request. \
                                    \n If no testers are available to be re-assigned, Reschedule the bookings to the \
                                    latest available time and then use the Force Approval option from requests.\
                                    \n (Note: On Force Approval, Tester will be released from his bookings on the requested date and the related customers will \
                                    be notified on the rescheduled date and time of their bookings.)") % str1)
                else:
                    self.status = 'approved'
        else:
            self.status = 'approved'

    def _send_notification_force_approve(self, req_obj, booking_ids):
        """docstring for _send_notification_force_approve"""
        # TODO send nofication to customer that tester is not available on the date and time by mustafa
        return True

    @api.multi
    def force_approve(self):
        """docstring for force_approve"""
        for req_obj in self:
            if req_obj.req_type != 'unavailability':
                raise Warning(
                    _('Overtime request is auto-approved. So, Force Approval need not be done.'))
            booking_ids = self._get_booking_list(req_obj)
            booking_name = ''
            for book_obj in booking_ids:
                if not booking_name:
                    booking_name = book_obj.booking_no
                else:
                    booking_name += ',' + book_obj.booking_no
            if not booking_name:
                raise ValidationError(_('Please use the Approve button instead of Force Approval.\
                \n Force Approval should only be done when a tester has a booking scheduled but is not available to perform \
                that due to request.'))
            if booking_name:
                # TODO send notification to customer and tester
                self._send_notification_force_approve(req_obj, booking_ids)
                # Also we release tester from those booking which found for
                # the particular tester
                for booking_id in booking_ids:
                    booking_id.write({'user_tester_id': False})
                req_obj.status = 'approved'
                return True

    def state_reject(self):
        self.status = 'reject'

    @api.one
    @api.depends('full_start_date', 'full_end_date', 'req_type')
    def onchange_full_date(self):
        if self.full_start_date and self.full_end_date:
            self.days_compute = int((datetime.strptime(self.full_end_date, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(self.full_start_date, DEFAULT_SERVER_DATE_FORMAT)).days) + 1

    @api.onchange('req_type')
    def onchange_req_type(self):
        if self.req_type == 'overtime':
            self.is_half_leave = True

    @api.onchange('full_start_date', 'full_end_date')
    def onchange_date(self):
        if self.full_start_date and self.full_end_date and self.is_half_leave == False:
            date_format = "%Y-%m-%d"
            a = datetime.strptime(self.full_start_date, date_format)
            b = datetime.strptime(self.full_end_date, date_format)
            delta = b - a
            self.days_compute = int(delta.days) + 1

    @api.model
    def my_requests(self):
        past_request = []
        upcoming_request = []
        requests = self.search_read([('user_id', '=', self._uid)], ['half_day_hour', 'req_no', 'req_type', 'description', 'start_date', 'end_date', 'full_start_date', 'full_end_date', 'is_half_leave', 'days_compute', 'duration_compute', 'status', 'ot_req_ids', 'overtime_start_time', 'overtime_end_time'])
        for request in requests:
            if request.get('ot_req_ids'):
                request['ot_req_ids'] = self.env['ot.request'].search_read([('id', 'in', request.get('ot_req_ids'))], ['ot_start_date', 'ot_end_date', 'duration', 'duration_compute'])
            if request.get('req_type') == 'unavailability' and request.get('is_half_leave') and (request.get('start_date') and request.get('end_date')):
                if datetime.strptime(request.get('start_date'), DEFAULT_SERVER_DATETIME_FORMAT) <= datetime.now() and datetime.strptime(request.get('end_date'), DEFAULT_SERVER_DATETIME_FORMAT) <= datetime.now():
                    past_request.append(request)
                else:
                    upcoming_request.append(request)
            elif request.get('req_type') == 'unavailability' and (not request.get('is_half_leave')) and (request.get('full_start_date') and request.get('full_end_date')):
                if datetime.strptime(request.get('full_start_date'), DEFAULT_SERVER_DATE_FORMAT) <= datetime.now() and datetime.strptime(request.get('full_end_date'), DEFAULT_SERVER_DATE_FORMAT) <= datetime.now():
                    past_request.append(request)
                else:
                    upcoming_request.append(request)
            elif request.get('req_type') == 'overtime':
                for overtime_rec in request.get('ot_req_ids'):
                    if overtime_rec.get('ot_start_date') and datetime.strptime(overtime_rec.get('ot_start_date'), DEFAULT_SERVER_DATETIME_FORMAT) >= datetime.now():
                        upcoming_request.append(request)
                        break
                    else:
                        past_request.append(request)
                        break
        return {'upcoming_request': upcoming_request, 'past_request': past_request}
