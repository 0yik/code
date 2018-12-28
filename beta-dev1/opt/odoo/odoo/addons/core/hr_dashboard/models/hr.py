# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Serpent Consulting Services Pvt. Ltd.
#    Copyright (C) 2017 OpenERP SA (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, \
DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    _description = "HR Employee"

    anniversary = fields.Integer(string = "Anniversary",
                                  compute = 'set_anniversary',
                                  store = True)

    @api.depends('join_date')
    def set_anniversary(self):
        cur_date = datetime.now()
        for emp in self:
            if emp.join_date:
                join_date = datetime.strptime(emp.join_date,
                                              DEFAULT_SERVER_DATE_FORMAT)
                rd = relativedelta(cur_date, join_date)
                emp.anniversary = rd.years


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    checkin_status = fields.Selection([('late', 'Late'),
                              ('ontime', 'Ontime'),
                              ('early', 'Early'),
                              ], string = 'CheckIn Status')
    checkin_diff = fields.Float(string = 'CheckIn Difference')
    checkout_status = fields.Selection([('late', 'Late'),
                              ('ontime', 'Ontime'),
                              ('early', 'Early'),
                              ], string = 'CheckOut Status')
    checkout_diff = fields.Float(string = 'CheckOut Difference')

    @api.model
    def get_diff(self, employee, checkin = False, checkout = False):
        # Fetch the cursor to execute the queries
        cr = self._cr
        user = self.env.user
        checkin_diff = check_in_status = checkout_diff = checkout_status = \
            False
        if checkin:
            # Fetch the Starting Hour for a particular day to Match against the
            # CheckIn
            check_in_dt = datetime.strptime(checkin,
                                            DEFAULT_SERVER_DATETIME_FORMAT)
            local_tz = pytz.timezone(user.tz or 'UTC')
            ci_dt = check_in_dt.replace(tzinfo = pytz.utc
                                         ).astimezone(local_tz)
            qry = '''select hour_from
                        from resource_calendar rc, \
                        resource_calendar_attendance rca
                        where rc.id = rca.calendar_id and
                        rc.id = %s and \
                        dayofweek=%s'''
            qry1 = qry + " and %s between date_from and date_to order by \
            hour_from limit 1"
            if not employee.calendar_id:
                raise ValidationError(_('Please Configure Working Time in Employee!'))
            params1 = (employee.calendar_id.id, str(ci_dt.weekday()), checkin)
            cr.execute(qry1, params1)
            res = cr.fetchone()
            # If specific dates are not given then fetch the records that do
            # not have dates
            if not res:
                qry2 = qry + " order by hour_from limit 1"
                params2 = (employee.calendar_id.id, str(ci_dt.weekday()))
                cr.execute(qry2, params2)
                res = cr.fetchone()
            hour_from = res and res[0] or 0.0
            # Converting the Hours and Minutes to Float to match as
            # odoo Standard.
            checkin_time = ci_dt.hour + (ci_dt.minute * 100 / 60) / 100.0

            # Get the Check In Difference
            checkin_diff = checkin_time - hour_from
            # Generate the CheckIn Status as per the CheckIn time
            check_in_status = 'ontime'
            if checkin_diff > 0:
                check_in_status = 'late'
            elif checkin_diff < 0:
                check_in_status = 'early'
        if checkout:
            # Fetch the Ending Hour for a particular day to Match against
            # the CheckOut
            check_out_dt = datetime.strptime(checkout,
                                             DEFAULT_SERVER_DATETIME_FORMAT)
            local_tz = pytz.timezone(user.tz or 'UTC')
            co_dt = check_out_dt.replace(tzinfo = pytz.utc
                                         ).astimezone(local_tz)
            qry = '''select hour_to,rca.id as rca_id
                        from resource_calendar rc, \
                        resource_calendar_attendance rca
                        where rc.id = rca.calendar_id and
                        rc.id = %s and \
                        dayofweek=%s'''
            qry1 = qry + "and %s between date_from and date_to order by \
                   hour_to desc limit 1"
            params1 = (employee.calendar_id.id, str(co_dt.weekday()), checkin)
            cr.execute(qry1, params1)
            res = cr.fetchone()
            # If specific dates are not given then fetch the records that do
            # not have dates
            if not res:
                qry2 = qry + " order by hour_to desc limit 1"
                params2 = (employee.calendar_id.id, str(co_dt.weekday()))
                cr.execute(qry2, params2)
                res = cr.fetchone()
            hour_to = res and res[0] or 0.0
            # Converting the Hours and Minutes to Float to match as
            # odoo Standard.
            checkout_time = co_dt.hour + (co_dt.minute * 100 / 60) / 100.0
            # Get the Check Out Difference
            checkout_diff = checkout_time - hour_to
            # Generate the CheckOut Status as per the CheckOut time
            checkout_status = 'ontime'
            if checkout_diff > 0:
                checkout_status = 'late'
            elif checkout_diff < 0:
                checkout_status = 'early'
        return checkin_diff, check_in_status, checkout_diff, checkout_status

    @api.model
    def create(self, vals):
        """
        Overridden create method to calculate the Check In/Check Out
        difference and status whether he is late, early or on time.
        -------------------------------------------------------------
        @param self : object pointer
        @param vals : a dictionary containing fields and their values
        """
        if vals.get('employee_id', False):
            emp_id = vals['employee_id']
            emp = self.env['hr.employee'].browse(emp_id)
            chk_in, chk_out = vals.get('check_in', False), \
                              vals.get('check_out', False)
            res = self.get_diff(emp, chk_in, chk_out)
            vals['checkin_diff'], vals['checkin_status'], \
            vals['checkout_diff'], vals['checkout_status'] = res
        return super(HRAttendance, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Overridden write method to calculate the Check In/Check Out
        difference and status whether he is late, early or on time.
        ------------------------------------------------------------
        @param self : object pointer
        @param vals : a dictionary containing fields and their values
        """
        emp_obj = self.env['hr.employee']
        if vals.get('check_in', False) or \
           vals.get('check_out', False) or \
           vals.get('employee_id', False):
            for att in self:
                emp = att.employee_id
                chk_in, chk_out = vals.get('check_in', False), \
                                 vals.get('check_out', False)
                # If Employee is Changed on the Attendance we need to check the
                # work schedule of the employee and regenerate the difference
                # and status
                emp_id = vals.get('employee_id', False)
                if emp_id:
                    emp = emp_obj.browse(emp_id)
                chk_in = chk_in or att.check_in
                chk_out = chk_out or att.check_out
                res = self.get_diff(emp, chk_in, chk_out)
                vals['checkin_diff'], vals['checkin_status'], \
                vals['checkout_diff'], vals['checkout_status'] = res
        return super(HRAttendance, self).write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
