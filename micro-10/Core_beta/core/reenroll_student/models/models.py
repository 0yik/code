# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StudentStudent(models.Model):
    _inherit = 'student.student'

    @api.multi
    def reenroll_student(self):
        for rec in self:
            rec.state = 'done'
        return True