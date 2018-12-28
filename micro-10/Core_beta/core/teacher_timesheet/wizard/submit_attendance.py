# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import ValidationError, Warning as UserError

class SubmitAttendanceWizard(models.TransientModel):
    _name = 'submit.attendance.wizard'
    
    @api.multi
    def submit_attendance_sheet(self):
        attendance_pool = self.env['daily.attendance']
        for active_id in self._context.get('active_ids'):
            attendance_obj = attendance_pool.browse(active_id)
            attendance_obj.write({'state': 'submitted'})
        return True

