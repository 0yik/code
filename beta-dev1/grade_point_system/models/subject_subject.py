# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class SubjectSubject(models.Model):
    _inherit = 'subject.subject'

    term_id = fields.Many2one("academic.month", string="Term")
    grade_id = fields.Many2one("grade.master", string="Grade")
    breakdown_line = fields.One2many("breakdown.weightage", "subject_id", string="Breakdown")
    weightage = fields.Integer("Weightage")
    
    @api.model
    def create(self, vals):
        result = super(SubjectSubject, self).create(vals)
        total_weightage = sum([x.weightage for x in result.breakdown_line])
        attendance_count = 0
        if vals.get('breakdown_line'):
            for breakdown_line in vals.get('breakdown_line'):
                if breakdown_line[2]['breakdown_type'] == 'Attendance':
                    attendance_count += 1
        if attendance_count > 1:
            raise UserError(_("You can't add Attendance Weightage line more then one !"))
        if total_weightage != 100:
            raise UserError(_("Total Weightage % must be 100"))
        return result
    
    @api.multi
    def write(self, vals):
        result = super(SubjectSubject, self).write(vals)
        total_weightage = sum([x.weightage for x in self.breakdown_line])
        attendance_count = 0
        if self.breakdown_line:
            for breakdown in self.breakdown_line:
                if breakdown.breakdown_type == 'Attendance':
                    attendance_count += 1
        if attendance_count > 1:
            raise UserError(_("You can't add Attendance Weightage line more then one !"))
        if total_weightage != 100:
            raise UserError(_("Total Weightage % must be 100"))
        return result
    
class BreakdownWeightage(models.Model):
    _name = 'breakdown.weightage'
    _rec_name = 'description'
    
    subject_id = fields.Many2one("subject.subject", string="Subject",ondelete='cascade')
    description = fields.Char("Description")
    breakdown_type = fields.Selection([('Exam', 'Exam'), ('Assignment', 'Assignment'),('Attendance', 'Attendance')],"Type")
    weightage = fields.Float("Weightage (%)")
    
