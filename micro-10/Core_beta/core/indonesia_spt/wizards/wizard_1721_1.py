from odoo import models, fields,api,_
from datetime import datetime
from dateutil import parser
from odoo.exceptions import ValidationError

class wizard_1721_1_report(models.TransientModel):
    _name = 'wizard.1721.1.report'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")

    @api.multi
    def print_report(self):
        if self.employee_ids:
            data = {'employee_ids': self.employee_ids, 'start_date': self.start_date, 'end_date': self.end_date}
        else:
            raise ValidationError(_('Please select employee'))

        return self.env['report'].get_action(self, 'indonesia_spt.report_1721_1',data={})
