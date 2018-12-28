# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class HrHoliday(models.Model):
    _inherit = 'hr.holidays'

    leave_cancel_id = fields.Many2one(
        comodel_name='hr.holidays.cancel',
        string='Leave Cancel', help='Ref. leave cancel', copy=False)

    @api.multi
    def name_get(self):
        res = super(HrHoliday, self).name_get()
        if not self._context.get('from_cancel'):
            return res
        res = []
        for leave in self:
            res.append((leave.id, _("%s : %.2f day(s) Date: %s to %s") % (
                leave.holiday_status_id.name, leave.number_of_days_temp,
                fields.Datetime.from_string(leave.date_from).strftime('%d/%m/%Y %H:%M'),
                fields.Datetime.from_string(leave.date_to).strftime('%d/%m/%Y %H:%M'))))
        return res

    @api.multi
    def name_get(self):
        res = super(HrHoliday, self).name_get()
        if not self._context.get('from_cancel'):
            return res
        res = []
        for leave in self:
            res.append((leave.id, _("%s : %.2f day(s) Date: %s to %s") % (
                leave.holiday_status_id.name, leave.number_of_days_temp,
                fields.Datetime.from_string(leave.date_from).strftime('%d/%m/%Y %H:%M'),
                fields.Datetime.from_string(leave.date_to).strftime('%d/%m/%Y %H:%M'))))
        return res

    @api.multi
    def action_leave_cancel(self):
        """docstring for action_leave_cancel"""
        holiday_cancel_obj = self.env['hr.holidays.cancel']
        for self_obj in self:
            cancel_id = holiday_cancel_obj.create({
                'employee_id': self_obj.employee_id.id,
                'name': self_obj.name,
                'date_from': self_obj.date_from,
                'date_to': self_obj.date_to,
                'holiday': self_obj.id,
                'report_note': self_obj.report_note,
            })
            self_obj.write({'leave_cancel_id': cancel_id.id})
        action = self.env.ref('hr_leave_cancel.open_cancel_holidays').read()[0]
        action['context'] = {'from_cancel': True}
        if len(cancel_id) > 1:
            action['domain'] = [('id', 'in', cancel_id.ids)]
        elif len(cancel_id) == 1:
            action['views'] = [(self.env.ref('hr_leave_cancel.edit_holiday_cancel').id, 'form')]
            action['res_id'] = cancel_id.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


HrHoliday()
