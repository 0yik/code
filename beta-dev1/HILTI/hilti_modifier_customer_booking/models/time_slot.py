# -*- coding: utf-8 -*-

from __future__ import division
from odoo import models, fields, api, _
import time
import pytz
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError, Warning
from unittest2.test.test_program import RESULT
# from ldif import start_time

def get_daily_slots(start, end, slot, date):
    dt = datetime.combine(date, datetime.strptime(start,"%H:%M:%S").time())
    slots = []
    while (dt.time() < datetime.strptime(end,"%H:%M:%S").time()):
        sl = [dt.strftime('%H:%M')]
        dt = dt + timedelta(minutes=slot)
        sl.append(dt.strftime('%H:%M'))
        slots.append(sl)
    return slots

class time_slot_start(models.Model):
    _name = 'time.slot.start'
    _rec_name = 'start_time'
    
    start_time = fields.Float('Start Time')
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            sp_name = str(record.start_time).split(".")
            name = ''.join(["%02d" % int(sp_name[0]),':', "%02d" % int(sp_name[1])])
            res.append((record.id, name))
        return res
    
    
class time_slot_end(models.Model):
    _name = 'time.slot.end'
    _rec_name = 'end_time'
    
    end_time = fields.Float('End Time')
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            sp_name = str(record.end_time).split(".")
            name = ''.join(["%02d" % int(sp_name[0]),':', "%02d" % int(sp_name[1])])
            res.append((record.id, name))
        return res
    

class time_slot_start_end(models.Model):
    _name = 'time.slot.start.end'
    _rec_name = "timeslot_start_id"
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            sp_name = str(record.timeslot_start_id.start_time).split(".")
            sp_name_co = ''.join(["%02d" % int(sp_name[0]),':', "%02d" % int(sp_name[1])])
            sn_name = str(record.timeslot_end_id.end_time).split(".")
            sn_name_co = ''.join(["%02d" % int(sn_name[0]),':', "%02d" % int(sn_name[1])])
            name = ''.join([str(sp_name_co) ,' - ', str(sn_name_co)])
            res.append((record.id, name))
        return res
    
    sequence = fields.Integer(default=10) 
    timeslot_start_id = fields.Many2one('time.slot.start', string="Start Time")
    timeslot_end_id = fields.Many2one('time.slot.end', string="End Time")
    start = fields.Float(related="timeslot_start_id.start_time", string="Start Time")
    end = fields.Float(related="timeslot_end_id.end_time", string="End Time")
    time_master_id = fields.Many2one('timeslot.master', string="End Time")
    
    
class time_slot_master(models.Model):
    _name = 'timeslot.master'
    _description = "Timeslot Management"
    
    name = fields.Char(string="Name")
    time_slot_based = fields.Boolean('Timeslot based on the time required per anchor')
    start_time = fields.Float("Start Time")
    end_time = fields.Float("End Time")
    segment_time = fields.Integer("Segment Time")
    
    
    calandar_display = fields.Integer('Display calendar month')
    time_slot_ids = fields.One2many('time.slot.start.end', 'time_master_id', string="Time Slot")
    
    def timeslot_calculation(self, vals):
        self.env['time.slot.start.end'].search([('time_master_id', '=', self.id)]).unlink()
        start_time = vals.get('start_time') or self.start_time
        end_time = vals.get('end_time') or self.end_time
        slot_time = vals.get('segment_time') or self.segment_time
        slots = get_daily_slots(start="%d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60), end="%d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60), slot=slot_time, date=datetime.now().date())
        for slot in slots:
            self.env['time.slot.start.end'].create({
                'timeslot_start_id': self.env['time.slot.start'].create({
                     'start_time': time.strptime(slot[0], "%H:%M").tm_hour + int(time.strptime(slot[0], "%H:%M").tm_min) / 60 
                }).id,
                'timeslot_end_id': self.env['time.slot.end'].create({
                    'end_time': time.strptime(slot[1], "%H:%M").tm_hour + int(time.strptime(slot[1], "%H:%M").tm_min) / 60
                }).id,
                'time_master_id': self.id 
            })
        return True
    
    @api.multi
    def write(self, vals):
        if ('start_time' in vals) or ('end_time' in vals) or ('segment_time' in vals):
            for rec in self:
                rec.timeslot_calculation(vals)
        else:
            vals.update({
                'start_time': 0.0,
                'end_time': 0.0,
                'segment_time': 0
            })
            for rec in self:
                rec.time_slot_ids.unlink()
        return super(time_slot_master, self).write(vals)
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('timeslot.master') or _('New')
        result = super(time_slot_master, self).create(vals)
        if ('start_time' in vals) or ('end_time' in vals) or ('segment_time' in vals):
            result.timeslot_calculation(vals)
        return result
    
    
class timeslot_booking(models.Model):
    _name = 'timeslot.booking'
    
    booking_date = fields.Date('Booking Date')
    time_slot_id = fields.Many2one('time.slot.start.end', string="Start and End Time")
    timeslot_start_id = fields.Many2one(related="time_slot_id.timeslot_start_id", string="Start Time")
    timeslot_end_id = fields.Many2one(related="time_slot_id.timeslot_end_id", string="End Time")
    start = fields.Float(related="timeslot_start_id.start_time", string="Start Time")
    end = fields.Float(related="timeslot_end_id.end_time", string="End Time")
    user_id = fields.Many2one('res.users', string="User")
    pr_booking_id = fields.Many2one('project.booking', string="Project Booking")
    temp = fields.Boolean(string="Temp")
    
    
    @api.onchange('booking_date')
    def onchange_booking_date(self):
        if self.booking_date:
            time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
            total_slot = [time.id for time in time_slot.time_slot_ids]
            booked_timesloat = self.search([('booking_date','=', self.booking_date)])
            total_book_slot = [book.time_slot_id.id for book in booked_timesloat]
            remaining_slot = [aa for aa in total_slot if aa not in total_book_slot]
            self.time_slot_id = False
            return {'domain': {'time_slot_id': [('id', 'in', remaining_slot)]}}
        else:
            self.time_slot_id = False
            return {'domain': {'time_slot_id': []}}
                    
    
    @api.model
    def create(self, vals):
        if 'is_reschedule' in self._context and self._context.get('is_reschedule'):
            old_booking_rec = self.search([('pr_booking_id', '=', self._context.get('default_pr_booking_id'))])
            if old_booking_rec:
                old_booking_rec.unlink()
        res = super(timeslot_booking, self).create(vals)
        return res
    
class holiday(models.Model):
    _name = 'holiday.holiday'
    
    holiday_date = fields.Date('Holiday Date')


class project_booking_anchor(models.Model):
    
    _name = 'project.booking.anchor'
    
    name = fields.Char(string="Anchor Number")
    anchor_type_id = fields.Many2one('anchor.type', string="Anchor Type")
    anchor_size_id = fields.Many2one('anchor.size', string="Anchor Size")
    anchor_qty = fields.Char(string="Anchor Quantity")
    project_booking_id = fields.Many2one('project.booking', string="Project Booking")
    feed_project_booking_id = fields.Many2one('project.booking', string="Project Booking")
    feedback_id = fields.Many2one('testing.feedback')
    failer_qty = fields.Char(string="Quantity Of Failures")
    an_complexity = fields.Selection([('simple', 'Simple'),('medium', 'Medium'),('complex', 'Complex')], string='Anchor complexity')
    
class project_booking(models.Model):
    _inherit = 'project.booking'
    
    
    time_booking_ids = fields.One2many('timeslot.booking', 'pr_booking_id', string="Booking Time")
    start_date_time = fields.Datetime('Start Date & Time')
    end_date_time = fields.Datetime('End Date & Time')
    booking_type = fields.Selection([('normal', 'Normal'),('special', 'Dedicated Support'),('last_minute', 'Last Minute'),('sic', 'SIC Request')], string='Booking Type')
    project_booking_anchor_ids = fields.One2many('project.booking.anchor', 'project_booking_id', string="Anchor Details")
    delay_time = fields.Float('Delay Duration', track_visibility='onchange')
    delay_remark = fields.Text('Delay Remarks', track_visibility='onchange')
    feedback_anchor_ids = fields.One2many('project.booking.anchor', 'feed_project_booking_id', string="FeedBack Anchor")
    testing_start_time = fields.Datetime('Actual Start Date & Time')
    testing_end_time = fields.Datetime('Actual End Date & Time')
    testing_duretion = fields.Char('Total Duration')
    testing_remark = fields.Char('Remarks')
    reminder_count = fields.Integer('Reminder Count')
    reminder_time = fields.Datetime('Last Reminder')
    reminder_history = fields.One2many('pt.reminder', 'pr_book_id', string="Reminder History")
    show_cancel_button = fields.Boolean('Show Cancel Button')
    is_cancel_from_tester = fields.Boolean('Cancel From Tester')
    
    @api.model
    def create(self, vals):
        result = super(project_booking, self).create(vals)
        if result:
            if result.booking_type in ['normal', 'sic']:
                total_line = [line.id for line in result.time_booking_ids]
                if len(total_line) > 1:
                    raise Warning(_("Booking should have only one timeslot."))
        template = self.env.ref('hilti_modifier_customer_booking.mail_template_booking_details')
        template.send_mail(result.id, force_send=True)
        return result
    
    @api.multi
    def write(self, vals):
        res = super(project_booking, self).write(vals)
        if self.booking_type in ['normal', 'sic']:
            total_line = [line.id for line in self.time_booking_ids]
            if len(total_line) > 1:
                raise Warning(_("Booking should have only one timeslot."))
        return res
    
    @api.multi
    def cancel_booking(self):
        self.check_date("Cancellation of booking is not allowed after reconfirmation. Please call Hilti admin for assistance on cancellation")
        self.sudo().write({'status': 'cancelled'})
        return True
    
    def final_booking_admin(self):
        self.is_final = True
    
    def check_date(self, msg='You can not reschedule the booking under 24 hours.'):
        start_datetime = ''
        end_datetime = ''
        if not self.env.user.tz:
            raise UserError(_('Please define timezone in current login user.'))
        now = datetime.now(pytz.timezone(self.env.user.tz)).replace(tzinfo=None)
        if self.booking_type == 'normal':
            if not self.time_booking_ids:
                raise UserError(_('Start datetime and End datetime is not defined.'))
            start_time = self.time_booking_ids[0].timeslot_start_id.start_time
            end_time = self.time_booking_ids[0].timeslot_end_id.end_time
            start_datetime = datetime.strptime(self.time_booking_ids[0].booking_date + ' ' + ("%d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60)), "%Y-%m-%d %H:%M:%S")  
            end_datetime = datetime.strptime(self.time_booking_ids[0].booking_date + ' ' + ("%d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60)), "%Y-%m-%d %H:%M:%S")  
        else:
            start_datetime = datetime.strptime(self.start_date_time, "%Y-%m-%d %H:%M:%S") 
            end_datetime = datetime.strptime(self.end_date_time, "%Y-%m-%d %H:%M:%S")
        if now >= start_datetime:
            raise UserError(_('You can not reschedule the booking of past date.'))
        if start_datetime <= (now + timedelta(hours=24)):
            raise UserError(_(msg))
        return True
    
    @api.onchange('partner_id')
    def onchange_partner_id_for_default(self):
        if self._context and 'booking_id_default' in self._context.keys():
            active_booking_id = self.search([('id', '=', self._context.get('booking_id_default'))])
            total_list = []
            for line in active_booking_id.project_booking_anchor_ids:
                anchor_dict = {'name': line.name, 'anchor_type_id': line.anchor_type_id and line.anchor_type_id.id or False,
                               'anchor_size_id': line.anchor_size_id and line.anchor_size_id.id or False, 'anchor_qty': line.anchor_qty,
                               'an_complexity': line.an_complexity}
                total_list.append(anchor_dict)
            if total_list:
                self.project_booking_anchor_ids = total_list
            
            
            
    @api.multi
    def rebook_booking(self):
        action = {}
        ctx = dict()
        form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_company', 'project_booking_view_admin_re_booking')[1]
        ctx.update({
            'default_booking_type': self.booking_type,
            'default_start_date_time': self.start_date_time,
            'default_end_date_time': self.end_date_time,
            'default_company_id': self.company_id and self.company_id.id,
            'default_project_id': self.project_id and self.project_id.id,
            'default_partner_id': self.partner_id and self.partner_id.id,
            'default_contact_id': self.contact_id,
            'default_contact_number': self.contact_number,
            'default_sid_required': self.sid_required,
            'default_location_id': self.location_id and self.location_id.id,
            'default_is_final': True,
            'booking_id_default': self.id,
            'come_from_default': 1,
            'default_create_date': str(datetime.now()),
        })
        action =  {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.booking',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            'target': 'new',
            'context': ctx,
        }
        return action
        
    
    @api.multi
    def reschedule_booking(self):
        self.check_date()
        action = {}
        ctx = dict()
        if self.booking_type == 'normal':
            ctx.update({
                'is_reschedule': True,
                'default_pr_booking_id': self.id
            })
            action = {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'timeslot.booking',
                'target': 'new',
                'context': ctx,
            }
        else:
            form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_customer_booking', 'reschedule_booking_form_view')[1]
            ctx.update({
                'booking_type': self.booking_type
            })
            action =  {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'reschedule.booking',
                'views': [(form_id, 'form')],
                'view_id': form_id,
                'target': 'new',
                'context': ctx,
            }
        return action
    
    def reassign_tester_from_admin(self):
        return True
    
    @api.multi
    def reconfirm_booking(self):
        self.check_date()
        compose_form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_customer_booking', 'reconfirm_booking_form_view')[1]
        ctx = dict()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reconfirm.booking',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    def start_testing(self):
        self.testing_start_time = datetime.today()
        self.status = 'started'
        
    def stop_testing(self):
        self.testing_end_time = datetime.today()
        if self.testing_start_time and self.testing_end_time:
            diff = datetime.strptime(self.testing_start_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(self.testing_end_time, "%Y-%m-%d %H:%M:%S")
            total_hm = abs(diff)
            self.testing_duretion = total_hm
            
    def cancel_booking_from_reminder(self):
        self.is_cancel_from_tester = True
        self.status = 'cancelled'
            
    def tester_reminder(self):
        reminder = self.env['admin.configuration'].search([], limit=1)
        send = False
        if not reminder.total_reminder > self.reminder_count:
            raise Warning(_("Reminder button to be clickable %s times.") % reminder.total_reminder)
        if not self.reminder_time:
            send = True
        else:
            now = datetime.today()
            now = str(now).split('.')[0]
            diff = datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S") - datetime.strptime(self.reminder_time, "%Y-%m-%d %H:%M:%S")
            total_hm = abs(diff)
            minutes = int(total_hm.total_seconds()/60)
            if minutes >= reminder.reminder_duration:
                send = True
            else:
                raise Warning(_("Reminder to stakeholders can be sent only after %s number of minutes.") % reminder.reminder_duration)
                send = False
        if reminder and reminder.total_reminder > self.reminder_count and send == True:
            self.reminder_count = self.reminder_count + 1
            all_partner = []
            if self.reminder_count == reminder.total_reminder:
                self.show_cancel_button = True
            all_partner_id = []
            all_partner.append(self.partner_id)
            all_partner_id.append(self.partner_id.id)
            if self.partner_id.account_manager_id and self.partner_id.account_manager_id.partner_id:
                all_partner.append(self.partner_id.account_manager_id.partner_id)
                all_partner_id.append(self.partner_id.account_manager_id.partner_id.id)
            for a in all_partner:
                self.reminder_time = datetime.now()
                ctx = dict(self._context or {})
                ctx['partner_email'] = a.id
                template = self.env.ref('hilti_modifier_customer_booking.email_template_for_reminder_id')
                template.with_context(ctx).send_mail(self.id, force_send=True)
            self.reminder_history = [(0,0,
                                         {'reminder_count': self.reminder_count,
                                          'reminder_time': self.reminder_time,
                                          'partner_ids': [(6,0, all_partner_id)]})]
            if self.reminder_count == reminder.total_reminder:
                self._cr.commit()
                raise UserError(_("You may cancel the booking as the customer is not responding to reminders."))
        
            
class pr_testing_reminder(models.Model):
    _name = 'pt.reminder'
    
    reminder_count = fields.Integer('Reminder No')
    reminder_time = fields.Datetime('Reminder Date & Time')
    pr_book_id = fields.Many2one('project.booking')
    partner_ids = fields.Many2many('res.partner', string="Stackholders")
    
            
        
        
    
    