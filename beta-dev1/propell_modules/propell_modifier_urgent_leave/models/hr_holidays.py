from odoo import api, fields, models
from odoo.exceptions import UserError

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    is_urgent = fields.Boolean(string='Urgent',track_visibility='onchange')
    report_note = fields.Text(string='HR Comments',track_visibility='onchange')

    @api.multi
    def action_approve(self):
        result = super(HrHolidays,self).action_approve()
        for holiday in self:
            if holiday.is_urgent != False and holiday.holiday_status_id.limit == True:
                return result

HrHolidays()