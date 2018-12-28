# -*- coding: utf-8 -*-

from odoo import api, models, _


class studentdetailenrolmentreport(models.AbstractModel):
    _name = 'report.atts_student_fields.report_student_nationality_enrolment'
    
    @api.multi
    def _student_nationality(self, date):
        nationality_dict = []
        total_asd=total_imid=total_mid=g_total =0
        nationality_obj = self.env['res.nationality']
        nationality_search_obj = nationality_obj.search([])
        student_obj = self.env['student.student']
        for nationality_id in nationality_search_obj:
            asd=imid=mid=total=name=0
            student_search_obj = student_obj.search([('state_custom','=','draft'),('nationality_id','=',nationality_id.id)])
            if student_search_obj:
                for student_id in student_search_obj:
                    if student_id.nationality_id:
                        name = student_id.nationality_id.name
                        student_programme = student_id.programme
                        if student_programme:
                            if student_programme == 'MID':
                                if mid==0:
                                    name=student_id.nationality_id.name
                                    mid=mid+1
                                    total_mid=total_mid+1
                                else:
                                    mid=mid+1
                                    total_mid=total_mid+1
                            if student_programme == 'Integrated':
                                if imid==0:
                                    name=student_id.nationality_id.name
                                    imid=imid+1
                                    total_imid=total_imid+1
                                else:
                                    imid=imid+1
                                    total_imid=total_imid+1
                            if student_programme == 'ASD':
                                if asd==0:
                                    name=student_id.nationality_id.name
                                    asd=asd+1
                                    total_asd=total_asd+1
                                else:
                                    asd=asd+1
                                    total_asd=total_asd+1
                            total=asd+mid+imid
                            g_total=total_asd+total_imid+total_mid
                    
            if name!=0:
                nationality_dict.append({'name': name,
                                      'asd': asd,
                                      'mid':mid,
                                      'imid':imid,
                                      'total':total
                                     })
        return nationality_dict,total_asd,total_imid,total_mid,g_total
    
    @api.multi
    def render_html(self, docids, data=None):
#        data.update({'date_selection': self.env['monthly.enrolment.wizard'].date_selection}) # self.env['monthly.enrolment.wizard'].context
        date_selection = data['form'].get('date_selection')
        self.model = self.env.context.get('active_model')
        docs = self.env['student.student'].browse(self.env.context.get('active_ids', []))
        student_obj = self.env['student.student']
        model = self.env.context.get('active_model')
        nationality_dict,total_asd,total_imid,total_mid,g_total = self._student_nationality(date_selection) 
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model or 'student.student',
            'docs': self.env['student.student'].browse(1),
            'nationality_dict':nationality_dict,
            'total_asd':total_asd,
            'total_imid':total_imid,
            'total_mid':total_mid,
            'g_total':g_total
        }
        return self.env['report'].render('atts_student_fields.report_student_nationality_enrolment', docargs)

