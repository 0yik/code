from odoo import fields,models,api, _
from datetime import datetime
from dateutil import rrule, parser
import logging
import math
_logger = logging.getLogger(__name__)


class overtime_rounding(models.Model):
    _name = 'overtime.rounding'

    active = fields.Boolean(string='Active')
    overtime_line_ids = fields.One2many('overtime.rounding.line','overtime_id',string='Overtime line')


class overtime_rounding_line(models.Model):
    _name = 'overtime.rounding.line'

    _rec_name = 'rounding'

    minite_from = fields.Integer(string='Minite From')
    minite_to = fields.Integer(string='Minite To')
    rounding = fields.Integer(string='Rounding')
    overtime_id = fields.Many2one('overtime.rounding',string='Rounding')

class hr_timesheet_sheet_sheet_day_inherit(models.Model):
    _inherit = "hr_timesheet_sheet.sheet.day"

    @api.multi
    def _compute_hours(self):
        overtime_ids = self.env['overtime.rounding'].search([('active', '=', True)], limit=1)
        for rec in self:
            period = {
                'date_from': rec.name,
                  'date_to': rec.name
            }
            dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(rec.name),
                                     until=parser.parse(rec.name)))

            for date_line in dates:
                dh = rec.sheet_id.calculate_duty_hours_ex(date_from=date_line,period=period)
                rec.contracthours = dh
                rec.overtimehours = rec.total_attendance - dh

                if rec.sheet_id:
                    overtime_hours = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.overtimehours * 60, 60))
                    overtime = datetime.strptime(overtime_hours, "%H:%M")
                    minute = datetime.strftime(overtime, "%M")
                    overtime_minute = int(minute)

                    if overtime_ids:
                        for overtime_id in overtime_ids.overtime_line_ids:
                            if overtime_minute >= overtime_id.minite_from and overtime_minute <= overtime_id.minite_to:
                                new_time = math.floor(rec.overtimehours)
                                overtime_rounding = float(overtime_id.rounding) / 100
                                rec.overtimehours = int(new_time) + overtime_rounding
                                a = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.overtimehours * 60, 60))
                                print a