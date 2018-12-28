from odoo import models, fields, api, _
from datetime import datetime, date


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def get_deliver_persons(self):
        result = []
        for employee in self.search([('department_id.name', '=', 'Deliveryman'), ('active', '=', True)]):
            documents = self.env['hr.employee.document'].search([('employee_ref', '=', employee.id)])
            valid_documents = documents.filtered(lambda r: fields.Date.from_string(r.expiry_date) >= date.today())
            if documents and len(documents) == len(valid_documents):
                intervals = employee.calendar_id.get_working_intervals_of_day(start_dt=datetime.now())
                for interval in intervals:
                    now = datetime.now()
                    if (now >= interval[0]) and (now <= interval[1]):
                        day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        if self.env['hr.attendance'].search([('check_in', '>=', fields.Datetime.to_string(day_start))]):
                            result.append({'id': employee.id, 'name': employee.name})
        return result
