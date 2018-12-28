# -*- coding: utf-8 -*-

from odoo import api, models, _


class studentdetailenrolmentreport(models.AbstractModel):
    _name = 'report.atts_student_fields.report_student_religion_enrolment'
    
    @api.multi
    def _student_religion(self):
        religion_dict = []
        cast_obj = self.env['student.cast']
        cast_search_obj = cast_obj.search([])
        student_obj = self.env['student.student']
        total=0
        for cast_obj in cast_search_obj:
            count=0
            name=0
            student_search_obj = student_obj.search([('state_custom','=','draft'),('religion_id','=',cast_obj.id)])
            if student_search_obj:
                for student_id in student_search_obj:
                    if student_id.religion_id:
                        if count==0:
                            name = student_id.religion_id.name
                            count=count+1
                            total=total+1
                        else:
                            count=count+1
                            total=total+1
            if name!=0:
                religion_dict.append({'name': name,
                                      'count': count,
                                     })
        return religion_dict,total
        
        
        
    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        model = self.env.context.get('active_model')
        religion_dict,total = self._student_religion() 
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model or 'student.student',
            'docs': self.env['student.student'].browse(1),
            'religion_dict':religion_dict,
            'total':total,
        }
        return self.env['report'].render('atts_student_fields.report_student_religion_enrolment', docargs)

