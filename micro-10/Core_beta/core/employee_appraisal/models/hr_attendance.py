# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import exceptions
from odoo.osv import osv
from datetime import date

class hr_attendance(models.Model):
    _inherit = "hr.attendance"
    _description = "Attendance"
    _rec_name = 'employee_code'

   
    @api.constrains('action')
    def _altern_si_so(self):
        """ Overridden method in order to overcome the pop up raising when saving the record.
        """
        return True
    
                
    employee_code = fields.Char('Employee ID')
    date = fields.Date('Date', default=date.today())
    absents = fields.Float('Absents',)
    late_cnts = fields.Float('Late Cnts')
    early_cnts = fields.Float('Early Cnt')
    rest = fields.Float('Rest')
    ph = fields.Float('PH')
    late_hrs = fields.Float('Late Hrs')
    early_hrs = fields.Float('Early Hrs')
    tot_brk_hrs = fields.Float('Tot Brk hrs')
    dedn = fields.Float('Dedn')
    half_days = fields.Float('Half Days')
    ot = fields.Float('OT')
    month = fields.Char('Month')
    year = fields.Many2one('hr.year','Year')
    total_abs = fields.Float('Total ABS')
    action = fields.Selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action', required=False)
    no_validation = fields.Boolean('No Validation Check')
    

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Inherited the Base Method to bypass the all below validations.
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            # TO BYPASS
            if attendance.no_validation:
            	break;
            # TO BYPASS Ends
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out >= attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    'empl_name': attendance.employee_id.name_related,
                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
                })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ])
                if no_check_out_attendances:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': attendance.employee_id.name_related,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                    })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<=', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name_related,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_attendance_before_check_out.check_in))),
                    })    

