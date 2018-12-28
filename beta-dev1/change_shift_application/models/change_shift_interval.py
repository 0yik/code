# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class change_shift_interval(models.Model):
    _name = 'change.shift.interval'
    _description= 'Recorded Change Shift Data'

    name = fields.Char('name')
    date_change = fields.Date('Changed Date')

    employee_id = fields.Many2one('hr.employee', string='Employee')
    schedule_id = fields.Many2one('resource.calendar', string='Schedule ID')

    attendance_root = fields.Many2many('resource.calendar.attendance',
                                      'resource_calendar_attendance_change_shift_root_rel', 'interval_id',
                                      'attendance_id', string='Attendance Root')
    attendance_change = fields.Many2many('resource.calendar.attendance',
                                        'resource_calendar_attendance_change_shift_change_rel', 'interval_id',
                                        'attendance_id', string='Attendance Change')
    attendance_new = fields.Many2many('resource.calendar.attendance',
                                       'resource_calendar_attendance_change_shift_new_rel', 'interval_id',
                                       'attendance_id', string='Attendance New')

    time_start_cycle = fields.Date('Start Cycle Date', help='This fields to tracking start date of Working Schedule Cycle')
    time_end_cycle = fields.Date('End Cycle Date', help='This fields to tracking end date of Working Schedule Cycle')
    check_changes = fields.Boolean('Changed', default=False)
    check_restored = fields.Boolean('Restored', default=False)

    @api.model
    def cron_do_changes(self):
        process_ids = self.search([('check_changes', '=', False)])
        for record in process_ids:
            record.process_attendance_schedule()
        return True

    @api.model
    def cron_do_restore(self):
        process_ids = self.search([('check_changes', '=', True),('check_restored', '=', False)])
        for record in process_ids:
            record.do_restore()
            record.check_restored = True
        return True

    @api.model
    def create(self, vals):
        res = super(change_shift_interval, self).create(vals)
        if vals.get('date_change', False) or vals.get('schedule_id'):
            res._get_cycle_start_time()
        return res

    def _get_cycle_start_time(self):
        date_change = fields.Datetime.from_string(self.date_change)
        if self.schedule_id and self.schedule_id.id:
            number_day = self.schedule_id.get_number_day_sequence(date_change)
            cycle_len = self.schedule_id.get_cycle_len()
            if number_day and cycle_len:
                #Vi Day Number bat dau tu 1 nen phai - 1 ngay
                start_date = date_change -  timedelta(days=(number_day - 1))
                end_date = date_change + timedelta(days=(cycle_len - 1))
                self.time_start_cycle = start_date
                self.time_end_cycle = end_date

    @api.model
    def process_attendance_schedule(self):
        check_date = self.check_date()
        if check_date:
            self.do_changes()
            self.check_changes = True

    @api.model
    def do_changes(self):
        day_number = False
        temp_id = self.env.ref('change_shift_application.resource_calendar_id').id
        try:
            day_number = self.attendance_root[0].day_seq
        except:
            date_change = fields.Datetime.from_string(self.date_change)
            day_number = self.schedule_id.get_number_day_sequence(date_change)
        if day_number:
            new_att = self.env['resource.calendar.attendance']
            for att in self.attendance_change:
                new_att += att.copy()
            new_att.write({'day_seq': day_number, 'calendar_id' : self.schedule_id.id})
            self.attendance_root.write({'calendar_id' : temp_id})
            self.attendance_new = new_att
        return

    @api.model
    def do_restore(self):
        self.attendance_root.write({'calendar_id' : self.schedule_id.id})
        self.attendance_new.unlink()
        return

    @api.model
    def check_date(self):
        now = datetime.now().date()
        date_change = fields.Datetime.from_string(self.date_change).date()
        start_cycle = fields.Datetime.from_string(self.time_start_cycle).date()
        end_cycle = fields.Datetime.from_string(self.time_end_cycle).date()
        if now < start_cycle or now > end_cycle or (now < end_cycle and now >= date_change):
            return False
        else:
            return True