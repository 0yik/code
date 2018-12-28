# -*- coding: utf-8 -*-

from odoo import api, models, _
from datetime import datetime, date

class TermlyUpdateseport(models.AbstractModel):
    _name = 'report.ap_intervention.report_ap_intervention'
    
    @api.multi
    def _termly_updates_report(self):
        dict_house_colour={}
        ap_intervation={}
        ot_list=[]
        temo_ot_list=[]
        st_list=[]
        temo_st_list=[]
        cm_list=[]
        temo_cm_list=[]
        header_ap_list=[]
        header_ap_list.append('')
        header_ap_list.append('')
        ot_h_list=[]
        st_h_list=[]
        cm_h_list=[]
        header_list=[]
        temp_header_dict={}
        ap_intervention_obj=self.env['ap.intervention']
        hr_employee_obj=self.env['hr.employee']
        ap_intervation_st = ap_intervention_obj.search([('referrel_type','=','st')])
        for st in ap_intervation_st:
            if st.ap_assigned.id:
                temo_st_list.append(st.ap_assigned.id)
                print st.ap_assigned.id
        st_list=list(set(temo_st_list))
        print st_list
        
        st_obj_dict={}
        for st_id in st_list:
            employee=hr_employee_obj.browse(st_id)
            st_obj_dict[st_id]=employee.name
            print employee
            header_ap_list.append(employee.name)
            st_h_list.append('')
        st_h_list=st_h_list[:-1]
        temp_header_dict['st']=st_obj_dict
        header_list.append(st_h_list)
        ap_intervation_ot = ap_intervention_obj.search([('referrel_type','=','ot')])
        for ot in ap_intervation_ot:
            if ot.ap_assigned.id:
                temo_ot_list.append(ot.ap_assigned.id)
                print ot.ap_assigned.id
        ot_list=list(set(temo_ot_list))
        print ot_list
        
        ot_obj_dict={}
        for ot_id in ot_list:
            employee=hr_employee_obj.browse(ot_id)
            ot_obj_dict[ot_id]=employee.name
            print employee
            header_ap_list.append(employee.name)
            ot_h_list.append('')
        ot_h_list=ot_h_list[:-1]
        temp_header_dict['ot']=ot_obj_dict
        header_list.append(ot_h_list)
        ap_intervation_cm = ap_intervention_obj.search([('referrel_type','=','cm')])
        for cm in ap_intervation_cm:
            if cm.ap_assigned.id:
                temo_cm_list.append(cm.ap_assigned.id)
                print cm.ap_assigned.id
        cm_list=list(set(temo_cm_list))
        print cm_list
        
        cm_obj_dict={}
        for cm_id in cm_list:
            employee=hr_employee_obj.browse(cm_id)
            cm_obj_dict[cm_id]=employee.name
            print employee
            header_ap_list.append(employee.name)
            cm_h_list.append('')
        cm_h_list=cm_h_list[:-1]
        header_list.append(cm_h_list)
        temp_header_dict['cm']=cm_obj_dict
        ap_intervation['headers']=header_list
        
        class_ids = self.env['class.class'].search([])
        class_dict={}
        class_list=[]
        class_list.append(header_ap_list)
        for class_id in class_ids:
            class_obj=self.env['class.class'].browse(class_id.id)
            print class_id.student_ids
            students_class_dict={}
            
            for student_id in class_id.student_ids:
                student_dict={}
                ap_dict={}
                student_list=[]
                print student_id
                empty_str='---'
                student_list.append(class_obj.name)
                student_obj = self.env['student.student'].browse(student_id.student_id.id)
                student_list.append(student_obj.name)
                ap_dict_st='---'
                ap_dict_ot='---'
                ap_dict_cm='---'
                for st in st_list:
                    ap_dict_st=empty_str
                    st_ap_intervation_student_ids=ap_intervention_obj.search([('ap_assigned','=',st)])
                    for st_ap_intervation_student_id in st_ap_intervation_student_ids:
                        st_ap_intervation_student_obj=ap_intervention_obj.browse(st_ap_intervation_student_id.id)
                        if st_ap_intervation_student_obj.referrel_type == 'st' and st_ap_intervation_student_obj.student_id.id == student_id.student_id.id:
                            if st_ap_intervation_student_obj.st_termly_updates:
                                ap_dict_st=str(st_ap_intervation_student_obj.st_termly_updates)
                    student_list.append(ap_dict_st)    
                            
                for ot in ot_list:
                    ap_dict_ot=empty_str
                    ot_ap_intervation_student_ids=ap_intervention_obj.search([('ap_assigned','=',ot)])
                    for ot_ap_intervation_student_id in ot_ap_intervation_student_ids:
                        ot_ap_intervation_student_obj=ap_intervention_obj.browse(ot_ap_intervation_student_id.id)
                        if ot_ap_intervation_student_obj.referrel_type == 'ot' and ot_ap_intervation_student_obj.student_id.id == student_id.student_id.id:
                            if ot_ap_intervation_student_obj.ot_termly_updates:
                                ap_dict_ot=str(ot_ap_intervation_student_obj.ot_termly_updates)
                    student_list.append(ap_dict_ot)
                                
                for cm in cm_list:
                    ap_dict_cm=empty_str
                    cm_ap_intervation_student_ids=ap_intervention_obj.search([('ap_assigned','=',ot)])
                    for cm_ap_intervation_student_id in cm_ap_intervation_student_ids:
                        cm_ap_intervation_student_obj=ap_intervention_obj.browse(cm_ap_intervation_student_id.id)
                        if cm_ap_intervation_student_obj.referrel_type == 'cm' and cm_ap_intervation_student_obj.student_id.id == student_id.student_id.id:
                            if cm_ap_intervation_student_obj.cm_termly_updates:
                                ap_dict_cm=str(cm_ap_intervation_student_obj.cm_termly_updates)
                    student_list.append(ap_dict_cm)
                    
                class_list.append(student_list)
            class_dict[class_obj.name]=students_class_dict
            print class_dict
        ap_intervation['data']=class_list
        print ap_intervation
        return ap_intervation
        
    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        model = self.env.context.get('active_model')
        termly_updates_dict = self._termly_updates_report() 
        headers=termly_updates_dict.get('headers')
        data=termly_updates_dict.get('data')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model or 'student.student',
            'docs': self.env['student.student'].browse(1),
            'headers':headers,
            'data':data
        }
        return self.env['report'].render('ap_intervention.report_ap_intervention', docargs)

