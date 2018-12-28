# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class hr_holidays(models.Model):
    _inherit = "hr.holidays"

    covering_staff = fields.Many2one('hr.employee', string='Covering Staff')
    change_shift_date = fields.Date('Changed Date')

    @api.onchange('date_from')
    def _onchange_date_from(self):
        res = super(hr_holidays, self)._onchange_date_from()
        if self.holiday_status_id and self.holiday_status_id.id == self.env.ref(
                'change_shift_application.change_shift_type').id:
            self.date_to = self.date_from
        return res

    @api.model
    def create_change_shift_interval(self):
        interval_obj = self.env['change.shift.interval']
        contract_id = self.get_contract_id()
        if len(contract_id) == 2 :
            attendance_emp_ids = self.get_attendance_ids(contract_id[0].working_hours, fields.Datetime.from_string(self.date_from))
            attendance_staff_ids = self.get_attendance_ids(contract_id[1].working_hours, fields.Datetime.from_string(self.change_shift_date))
            if attendance_emp_ids and attendance_staff_ids:
                interval_id1 = interval_obj.create({
                    'name' : self.name,
                    'date_change' : self.date_from,
                    'employee_id' : self.employee_id.id,
                    'attendance_root' : [(6, 0, attendance_emp_ids)],
                    'attendance_change': [(6, 0, attendance_staff_ids)],
                    'schedule_id' : contract_id[0].working_hours.id,
                })
                interval_id2 = interval_obj.create({
                    'name': self.name,
                    'date_change': self.change_shift_date,
                    'employee_id': self.covering_staff.id,
                    'attendance_root': [(6, 0, attendance_staff_ids)],
                    'attendance_change': [(6, 0, attendance_emp_ids)],
                    'schedule_id': contract_id[1].working_hours.id,
                })
        return

    @api.model
    def get_attendance_ids(self, schedule, time):
        if schedule and time:
            attendance_ids = schedule.get_attendances_for_weekday(time)
            return attendance_ids.ids or []

    @api.model
    def get_contract_id(self):
        contract_obj = self.env['hr.contract']
        now = datetime.now().date()
        contracts = []
        if self.employee_id and self.employee_id.id:
            contract_id = contract_obj.search(
                [('employee_id', '=', self.employee_id.id), ('date_start', '<=', now),'|',('date_end', '>=', now), ('date_end', '=', False),
                 ('working_hours', '!=', False)], limit=1)
            if contract_id:
                contracts.append(contract_id)
        if self.covering_staff and self.covering_staff.id:
            contract_id = contract_obj.search(
                [('employee_id', '=', self.covering_staff.id), ('date_start', '<=', now), '|',('date_end', '>=', now), ('date_end', '=', False),
                 ('working_hours', '!=', False)], limit=1)
            if contract_id:
                contracts.append(contract_id)
        return contracts
