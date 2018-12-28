# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class HrHolidayStatus(models.Model):
    _inherit = 'hr.holidays.status'

    leave_attachment = fields.Boolean(
        string='Leave Attachment',
        help='If checked, attachment is compulsory for the leave request.')


HrHolidayStatus()


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def action_confirm(self):
        attachment_ids = self.env['ir.attachment'].search(
            [('res_model', '=', 'hr.holidays'),
             ('res_id', 'in', self.ids),
             ])
        if self.holiday_status_id.leave_attachment and not attachment_ids:
            raise exceptions.ValidationError(_('Leave attachment is compulsory for the leave request.'))
        res = super(HrHolidays, self).action_confirm()
        return res
