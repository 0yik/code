# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import datetime
from datetime import timedelta, date;

class allocate_leave(models.TransientModel):

    _inherit = 'allocate.leaves'

    leave_expiry = fields.Boolean(string="Leave Expiry")
    leave_expiry_day=fields.Integer(string="No. of days")
    effective_date=fields.Date(string="Effective Date")


    @api.multi
    def allocate_leaves(self):
    	d1= date.today()
        if self.effective_date:
            d1= datetime.datetime.strptime(self.effective_date,"%Y-%m-%d").date()
        else:
            d1= date.today()
        if self.leave_expiry_day>=0:
            d2= str(d1 + timedelta(days=self.leave_expiry_day))
        else:
            d2=False
        import pdb; pdb.set_trace()
        for emp in self.employee_ids:
            leave_rec = []
            if emp.leave_config_id and emp.leave_config_id.holiday_group_config_line_ids:
                for leave in emp.leave_config_id.holiday_group_config_line_ids:
                    leave_rec.append(leave.leave_type_id.id)
                if self.holiday_status_id.id in leave_rec:
                    vals = {
                        'name' : 'Assign Default ' + str(self.holiday_status_id.name2),
                        'holiday_status_id': self.holiday_status_id.id, 
                        'type': self.type,
                        'employee_id': emp.id,
                        'number_of_days_temp': self.no_of_days,
                        'state': 'confirm',
                        'holiday_type' : 'employee',
                        'hr_year_id':self.fiscal_year_id.id,
                       	'expiry_date':d2,
                        'leave_expiry':self.leave_expiry,
                        'effective_date':self.effective_date,
                        'leave_expiry_day':self.leave_expiry_day
                        }
                    self.env['hr.holidays'].create(vals)
        return True


