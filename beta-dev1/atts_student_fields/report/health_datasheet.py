# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import collections
import datetime


class enrolment_by_gender_report(models.AbstractModel):
    _name = 'report.atts_student_fields.health_datasheet_report_temp'
    
    
    @api.multi
    def _current_date_year(self):
        data={}
        date=datetime.date.today()
        data["current_date"]=date
        data["current_year"]=date.year
        
        return data
    
    
    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env['student.student'].browse(self.env.context.get('active_ids', []))
        student_obj = self.env['student.student']
        student_search_obj = student_obj.search([])
        model = self.env.context.get('active_model')
        current_date_year = self._current_date_year()
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model or 'student.student',
            'docs': self.env['student.student'].browse(docids),
            'current_date_year':current_date_year
        }
        return self.env['report'].render('atts_student_fields.health_datasheet_report_temp', docargs)






