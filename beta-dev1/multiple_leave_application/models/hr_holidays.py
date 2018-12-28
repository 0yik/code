# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError
HOURS_PER_DAY = 8


class hr_holidays_multiple(models.Model):
    _name = "hr.holidays.multiple"
    _inherit = "hr.holidays"

    holiday_line_ids = fields.One2many('hr.holidays', 'holidays_multiple_ids', string='Line Ids')
    holiday_status_id   = fields.Many2one('hr.holidays.status',required=True)

    # @api.onchange('holiday_status_id')
    # def onchange_status

    @api.constrains('date_from', 'date_to', 'holiday_status_id')
    def _check_public_holiday_leave(self):
        if self._name == 'hr.holidays.multiple':
            return
        for rec in self:
            if rec.type == 'remove':
                if rec.holiday_status_id and rec.holiday_status_id.id and rec.holiday_status_id.count_days_by:
                    if rec.holiday_status_id.count_days_by == 'working_days_only':
                        diff_day = rec._check_holiday_to_from_dates(rec.date_from, rec.date_to, rec.employee_id.id)
                        if diff_day == 0:
                            raise ValidationError(_('You are not able to apply leave Request on Holiday.!'))

    # def _onchange_holiday_status_id(self):
    #     # self.holiday_line_ids.holiday_status_id=self.holiday_status_id
    #     print
    #     print(self.holiday_line_ids.holiday_status_id)


    @api.onchange('name', 'holiday_status_id', 'holiday_type', 'employee_id', 'category_id', 'department_id',
                  'payslip_status', 'notes', 'report_note')
    def onchange_some_field(self):
        list  = ['name', 'holiday_status_id', 'holiday_type', 'employee_id', 'category_id', 'department_id',
                  'payslip_status', 'notes', 'report_note']
        datas = []
        for field_name in list:
            datas.append((field_name, self[field_name]))

        if self.holiday_line_ids:
            for line in self.holiday_line_ids:
                for data in datas:
                    line[data[0]] =  data[1]
    @api.multi
    def action_confirm(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        for record in self:
            for line in record.holiday_line_ids:
                line.action_confirm()
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state != 'confirm':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                holiday.action_validate()

    @api.multi
    def action_validate(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'manager_id2': manager.id})
            else:
                holiday.write({'manager_id': manager.id})
            for line in holiday.holiday_line_ids:
                line.action_validate()
        return True

    @api.multi
    def action_refuse(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'manager_id': manager.id})
            else:
                holiday.write({'state': 'refuse', 'manager_id2': manager.id})

            for line in holiday.holiday_line_ids:
                line.action_refuse()
                self._cr.commit()
        return True

    @api.multi
    def action_draft(self):
        for holiday in self:
            if not holiday.can_reset:
                raise UserError(_('Only an HR Manager or the concerned employee can reset to draft.'))
            if holiday.state not in ['confirm', 'refuse']:
                raise UserError(_('Leave request state must be "Refused" or "To Approve" in order to reset to Draft.'))
            holiday.write({
                'state': 'draft',
                'manager_id': False,
                'manager_id2': False,
            })
            for line in holiday.holiday_line_ids:
                line.action_draft()
        return True

    @api.model
    def create(self, vals):
        # self.onchange_some_field()
        # if self.holiday_line_ids:
        #
        #     vals['holiday_line_ids.holiday_status_id'] = self.holiday_status_id.id
        # self.onchange_some_field()
        # i = range(len(vals['holiday_line_ids']))
        for i in range(len(vals['holiday_line_ids'])):
            vals['holiday_line_ids'][i][2]['holiday_status_id'] = vals['holiday_status_id']
        # vals['holiday_line_ids.holiday_status_id'] = vals['holiday_status_id']
        res = super(hr_holidays_multiple, self).create(vals)
        self.re_compute_all_line(res.holiday_line_ids)
        self.onchange_some_field()
        return res

    @api.multi
    def write(self, vals):
        # self.onchange_some_field()
        # if self.holiday_line_ids:
        #    for line in self.holiday_line_ids:

        res = super(hr_holidays_multiple, self).write(vals)

        for record in self:
            self.re_compute_all_line(record.holiday_line_ids)
        return res

    @api.model
    def re_compute_all_line(self, lines):
        #because default Duration is readonly, so we can't use onchange, need recompute
        for line in lines:
            date_from = line.date_from
            date_to = line.date_to

            # No date_to set so far: automatically compute one 8 hours later
            if date_from and not date_to:
                date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
                line.date_to = str(date_to_with_delta)

            # Compute and update the number of days
            if (date_to and date_from) and (date_from <= date_to):
                line.number_of_days_temp = line._get_number_of_days(date_from, date_to, line.employee_id.id)
            else:
                line.number_of_days_temp = 0
        return

class hr_holidays(models.Model):
    _inherit = "hr.holidays"

    holiday_status_id     = fields.Many2one('hr.holidays.status',required=False)

    # def _holiday_status_id_update(self):
    #     if self._name == 'hr.holidays':
    #         return False
    #     if self._name == 'hr.holidays.multiple':
    #         for line in self.holiday_line_ids:
    #             line.holiday_status_id = self.holiday_status_id.id

    holidays_multiple_ids = fields.Many2one('hr.holidays.multiple', string='Mutiple Holiday Id')
    half_day = fields.Boolean('Half Day')
    am_check = fields.Boolean('AM')
    pm_check = fields.Boolean('PM')
    older_date_from = fields.Datetime('Older Date From')
    older_date_to = fields.Datetime('Older Date To')
    # holiday_status_id   = fields.Many2one('hr.holidays.status',related='holidays_multiple_ids.holiday_status_id')

    @api.onchange('am_check')
    def onchange_am_check(self):
        for record in self:
            if record.am_check:
                record.older_date_to = record.date_to
                record.older_date_from = record.date_from
                if record.date_to:
                    date_to = datetime.strptime(record.date_to, '%Y-%m-%d %H:%M:%S')
                    date_to = date_to.strftime('%Y-%m-%d 04:00:00')
                    record.date_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
                if record.date_from:
                    date_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
                    record.date_from = date_to - timedelta(hours=5)
            else:
                record.date_to = record.older_date_to
                record.date_from = record.older_date_from

    @api.onchange('pm_check')
    def onchange_pm_check(self):
        for record in self:
            if record.pm_check:
                record.older_date_to = record.date_to
                record.older_date_from = record.date_from
                if record.date_from:
                    date_from = datetime.strptime(record.date_from, '%Y-%m-%d %H:%M:%S')
                    date_from = date_from.strftime('%Y-%m-%d 04:00:00')
                    record.date_from = date_from
                if record.date_to:
                    date_to = datetime.strptime(record.date_to, '%Y-%m-%d %H:%M:%S')
                    date_to = date_to.strftime('%Y-%m-%d 11:00:00')
                    record.date_to = date_to
            else:
                record.date_to = record.older_date_to
                record.date_from = record.older_date_from

    # def write(self,vals):
    #     if self._name == 'hr.holidays.multiple':
    #         res = super(hr_holidays,self).write(vals)
    #         return res
    #     if self._name == 'hr.holidays':
    #         if self.holidays_multiple_ids:
    #             vals['holiday_status_id']= self.holidays_multiple_ids.holiday_status_id.id
    #             res = super(hr_holidays,self).write(vals)
    #             return res

    # @api.model
    # def create(self,vals):
    #     # if self._name == 'hr.holidays.multiple':
    #     #     res = super(hr_holidays,self).create(vals)
    #     #     return res
    #     # if self._name == 'hr.holidays':
    #     #     if self.holidays_multiple_ids:
    #     #         vals['holiday_status_id']= self.holidays_multiple_ids.holiday_status_id.id
    #     #         res = super(hr_holidays,self).create(vals)
    #     #         return res
    #     res = super(hr_holidays, self).create(vals)
    #     return res