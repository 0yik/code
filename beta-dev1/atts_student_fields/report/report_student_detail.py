# -*- coding: utf-8 -*-

from odoo import api, models, _
import time
import collections
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from dateutil import parser
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class studentdetailreport(models.AbstractModel):
    _name = 'report.atts_student_fields.report_studentdetail'
    
    def _total_no(self):
        dict = {}
        integrated_list = []
        mid_list = []
        asd_list = []
        age_7 = []
        age_8 = []
        age_9 = []
        age_10 = []
        age_11 = []
        age_12 = []
        age_13 = []
        age_14 = []
        age_15 = []
        age_16 = []
        age_17 = []
        age_18 = []
        student_obj = self.env['student.student']
        student_search_obj = student_obj.search([('state_custom','=','draft')])
        for student_obj in student_search_obj:
            student_programme = student_obj.programme
            student_age = student_obj.age
            if student_programme and student_age:
                if student_programme == 'Integrated':
                    integrated_list.append(student_programme)
                if student_programme == 'ASD':
                    asd_list.append(student_programme)
                if student_programme == 'MID':
                    mid_list.append(student_programme)
                if student_age == 7:
                    student_programme_7 = student_programme
                    age_7.append(student_programme_7)
                if student_age == 8:   
                    student_programme_8 = student_programme
                    age_8.append(student_programme_8)
                if student_age == 9:
                    student_programme_9 = student_programme
                    age_9.append(student_programme_9)
                if student_age == 10:
                    student_programme_10 = student_programme
                    age_10.append(student_programme_10)
                if student_age == 11:
                    student_programme_11 = student_programme
                    age_11.append(student_programme_11)
                if student_age == 12:   
                    student_programme_12 = student_programme
                    age_12.append(student_programme_12)
                if student_age == 13:
                    student_programme_13 = student_programme
                    age_13.append(student_programme_13)
                if student_age == 14:
                    student_programme_14 = student_programme
                    age_14.append(student_programme_14)
                if student_age == 15:
                    student_programme_15 = student_programme
                    age_15.append(student_programme_15)
                if student_age == 16:   
                    student_programme_16 = student_programme
                    age_16.append(student_programme_16)
                if student_age == 17:
                    student_programme_17 = student_programme
                    age_17.append(student_programme_17)
                if student_age == 18:    
                    student_programme_18 = student_programme
                    age_18.append(student_programme_18)   
        dict['7'] = len(age_7)
        dict['8'] = len(age_8)
        dict['9'] = len(age_9)
        dict['10'] = len(age_10)
        dict['11'] = len(age_11)
        dict['12'] = len(age_12)
        dict['13'] = len(age_13)
        dict['14'] = len(age_14)
        dict['15'] = len(age_15)
        dict['16'] = len(age_16)
        dict['17'] = len(age_17)
        dict['18'] = len(age_18)
        dict['integrated_total'] = len(integrated_list)
        dict['asd_total'] = len(asd_list)
        dict['mid_total'] = len(mid_list)
        dict['grand_total'] = len(integrated_list) + len(asd_list) + len(mid_list)
        return dict
    
    def _age_ids(self, date_selection):
        integrated_list = []
        asd_list = []
        mid_list = []
        age_integrated_list = []
        age_asd_list = []
        age_mid_list = []
        year_list = []
        age_7i = []
        age_8i = []
        age_9i = []
        age_10i = []
        age_11i = []
        age_12i = []
        age_13i = []
        age_14i = []
        age_15i = []
        age_16i = []
        age_17i = []
        age_18i = []
        
        age_7a = []
        age_8a = []
        age_9a = []
        age_10a = []
        age_11a = []
        age_12a = []
        age_13a = []
        age_14a = []
        age_15a = []
        age_16a = []
        age_17a = []
        age_18a = []
        
        age_7 = []
        age_8 = []
        age_9 = []
        age_10 = []
        age_11 = []
        age_12 = []
        age_13 = []
        age_14 = []
        age_15 = []
        age_16 = []
        age_17 = []
        age_18 = []
        
        age_7_dicti = {}
        age_8_dicti = {}
        age_9_dicti = {}
        age_10_dicti = {}
        age_11_dicti = {}
        age_12_dicti = {}
        age_13_dicti = {}
        age_14_dicti = {}
        age_15_dicti = {}
        age_16_dicti = {}
        age_17_dicti = {}
        age_18_dicti = {}
        
        age_7_dicta = {}
        age_8_dicta = {}
        age_9_dicta = {}
        age_10_dicta = {}
        age_11_dicta = {}
        age_12_dicta = {}
        age_13_dicta = {}
        age_14_dicta = {}
        age_15_dicta = {}
        age_16_dicta = {}
        age_17_dicta = {}
        age_18_dicta = {}
        
        age_7_dict = {}
        age_8_dict = {}
        age_9_dict = {}
        age_10_dict = {}
        age_11_dict = {}
        age_12_dict = {}
        age_13_dict = {}
        age_14_dict = {}
        age_15_dict = {}
        age_16_dict = {}
        age_17_dict = {}
        age_18_dict = {}
        integrated_dict = {}
        mid_dict = {}
        asd_dict = {}
        student_obj = self.env['student.student']
        student_search_obj = student_obj.search([('state_custom','=','draft')])  # 2017-10-06
        date = str(date_selection)
        enrolment_year = date.split('-')[0]
        enrolment_month = date.split('-')[1]
        enrolment_month = calendar.month_abbr[int(enrolment_month) - 1]
        # enrolment_month=date+ relativedelta(months=int(enrolment_month)-1)
        year = date.split('-')[0]
        year = int(year)
        year -= 7
        for i in range(12):
            if i == 0:
                year -= 0
            else:
                year -= 1
            year_list.append(year)
        for student_obj in student_search_obj:
            student_programme = student_obj.programme
            if student_programme == 'Integrated':
                student_integrated_age = student_obj.age
                if student_integrated_age == 7:
                    age_7i.append(student_integrated_age)
                    age_7_dicti['7'] = len(age_7i)
                    age_integrated_list.append(age_7_dicti)
                if student_integrated_age == 8:
                    age_8i.append(student_integrated_age)
                    age_8_dicti['8'] = len(age_8i)
                    age_integrated_list.append(age_8_dicti)
                if student_integrated_age == 9:
                    age_9i.append(student_integrated_age)
                    age_9_dicti['9'] = len(age_9i)
                    age_integrated_list.append(age_9_dicti)
                if student_integrated_age == 10:
                    age_10i.append(student_integrated_age)
                    age_10_dicti['10'] = len(age_10i)
                    age_integrated_list.append(age_10_dicti)
                if student_integrated_age == 11:
                    age_11i.append(student_integrated_age)
                    age_11_dicti['11'] = len(age_11i)
                    age_integrated_list.append(age_11_dicti)
                if student_integrated_age == 12:   
                    age_12i.append(student_integrated_age)
                    age_12_dicti['12'] = len(age_12i)
                    age_integrated_list.append(age_12_dicti)
                if student_integrated_age == 13:
                    age_13i.append(student_integrated_age)
                    age_13_dicti['13'] = len(age_13i)
                    age_integrated_list.append(age_13_dicti)
                if student_integrated_age == 14:
                    age_14i.append(student_integrated_age)
                    age_14_dicti['14'] = len(age_14i)
                    age_integrated_list.append(age_14_dicti)
                if student_integrated_age == 15:
                    age_15i.append(student_integrated_age)
                    age_15_dicti['15'] = len(age_15i)
                    age_integrated_list.append(age_15_dicti)
                if student_integrated_age == 16:   
                    age_16i.append(student_integrated_age)
                    age_16_dicti['16'] = len(age_16i)
                    age_integrated_list.append(age_16_dicti)
                if student_integrated_age == 17:
                    age_17i.append(student_integrated_age)
                    age_17_dicti['17'] = len(age_17i)
                    age_integrated_list.append(age_17_dicti)
                if student_integrated_age == 18:    
                    age_18i.append(student_integrated_age)
                    age_18_dicti['18'] = len(age_18i)
                    age_integrated_list.append(age_18_dicti)
            if student_programme == 'ASD':
                student_asd_age = student_obj.age
                if student_asd_age == 7:
                    age_7a.append(student_asd_age)
                    age_7_dicta['7'] = len(age_7a)
                    age_asd_list.append(age_7_dicta)
                if student_asd_age == 8:
                    age_8a.append(student_asd_age)
                    age_8_dicta['8'] = len(age_8a)
                    age_asd_list.append(age_8_dicta)
                if student_asd_age == 9:
                    age_9a.append(student_asd_age)
                    age_9_dicta['9'] = len(age_9a)
                    age_asd_list.append(age_9_dicta)
                if student_asd_age == 10:
                    age_10a.append(student_asd_age)
                    age_10_dicta['10'] = len(age_10a)
                    age_asd_list.append(age_10_dicta)
                if student_asd_age == 11:
                    age_11a.append(student_asd_age)
                    age_11_dicta['11'] = len(age_11a)
                    age_asd_list.append(age_11_dicta)
                if student_asd_age == 12:   
                    age_12a.append(student_asd_age)
                    age_12_dicta['12'] = len(age_12a)
                    age_asd_list.append(age_12_dicta)
                if student_asd_age == 13:
                    age_13a.append(student_asd_age)
                    age_13_dicta['13'] = len(age_13a)
                    age_asd_list.append(age_13_dicta)
                if student_asd_age == 14:
                    age_14a.append(student_asd_age)
                    age_14_dicta['14'] = len(age_14a)
                    age_asd_list.append(age_14_dicta)
                if student_asd_age == 15:
                    age_15a.append(student_asd_age)
                    age_15_dicta['15'] = len(age_15a)
                    age_asd_list.append(age_15_dicta)
                if student_asd_age == 16:   
                    age_16a.append(student_asd_age)
                    age_16_dicta['16'] = len(age_16a)
                    age_asd_list.append(age_16_dicta)
                if student_asd_age == 17:
                    age_17a.append(student_asd_age)
                    age_17_dicta['17'] = len(age_17a)
                    age_asd_list.append(age_17_dicta)
                if student_asd_age == 18:    
                    age_18a.append(student_integrated_age)
                    age_18_dicta['18'] = len(age_18a)
                    age_asd_list.append(age_18_dicta)
            if student_programme == 'MID':
                student_mid_age = student_obj.age
                if student_mid_age == 7:
                    age_7.append(student_mid_age)
                    age_7_dict['7'] = len(age_7)
                    age_mid_list.append(age_7_dict)
                if student_mid_age == 8:
                    age_8.append(student_mid_age)
                    age_8_dict['8'] = len(age_8)
                    age_mid_list.append(age_8_dict)
                if student_mid_age == 9:
                    age_9.append(student_mid_age)
                    age_9_dict['9'] = len(age_9)
                    age_mid_list.append(age_9_dict)
                if student_mid_age == 10:
                    age_10.append(student_mid_age)
                    age_10_dict['10'] = len(age_10)
                    age_mid_list.append(age_10_dict)
                if student_mid_age == 11:
                    age_11.append(student_mid_age)
                    age_11_dict['11'] = len(age_11)
                    age_mid_list.append(age_11_dict)
                if student_mid_age == 12:   
                    age_12.append(student_mid_age)
                    age_12_dict['12'] = len(age_12)
                    age_mid_list.append(age_12_dict)
                if student_mid_age == 13:
                    age_13.append(student_mid_age)
                    age_13_dict['13'] = len(age_13)
                    age_mid_list.append(age_13_dict)
                if student_mid_age == 14:
                    age_14.append(student_mid_age)
                    age_14_dict['14'] = len(age_14)
                    age_mid_list.append(age_14_dict)
                if student_mid_age == 15:
                    age_15.append(student_mid_age)
                    age_15_dict['15'] = len(age_15)
                    age_mid_list.append(age_15_dict)
                if student_mid_age == 16:   
                    age_16.append(student_mid_age)
                    age_16_dict['16'] = len(age_16)
                    age_mid_list.append(age_16_dict)
                if student_mid_age == 17:
                    age_17.append(student_mid_age)
                    age_17_dict['17'] = len(age_17)
                    age_mid_list.append(age_17_dict)
                if student_mid_age == 18:    
                    age_18.append(student_mid_age)
                    age_18_dict['18'] = len(age_18)
                    age_mid_list.append(age_18_dict)
        for age_dict in age_integrated_list:
            if age_dict not in integrated_list:
                integrated_list.append(age_dict)
        for age_dict in age_mid_list:
            if age_dict not in mid_list:
                mid_list.append(age_dict)
        for age_dict in age_asd_list:
            if age_dict not in asd_list:
                asd_list.append(age_dict)
        integrated_dict['Integrated'] = integrated_list
        mid_dict['MID'] = mid_list
        asd_dict['ASD'] = asd_list
        return enrolment_year, enrolment_month, year_list , integrated_dict , mid_dict, asd_dict
    
    @api.multi
    def _total_admitted_student_previous_month(self, data):
        mid_name = []
        asd_name = []
        integrated_name = []
        mid_withdraw_name = []
        asd_withdraw_name = []
        integrated_withdraw_name = []
        withdraw_integrated_list = []
        withdraw_asd_list = []
        withdraw_mid_list = []
        integrated_list = []
        asd_list = []
        mid_list = []
        programme_dict = {}  
        student_obj = self.env['student.student']
        selected_date = data
        split_date = selected_date.split('-')
        today = datetime.strptime(selected_date, DF).date()  # selected date converted to date 
        first = today.replace(day=1)  # 1st of selected month
        last_day_selected_month = calendar.monthrange(int(split_date[0]), int(split_date[1]))
        last_day_selected_month = last_day_selected_month[1]
        last_day_selected_month_date = first.replace(day=last_day_selected_month)
        lastMonth = first - timedelta(days=1)
        lastMonth = lastMonth.replace(day=1)
        ###########3333
        lastMonth_str = str(lastMonth).split('-')
        split = calendar.monthrange(int(lastMonth_str[0]), int(lastMonth_str[1]))
        split = split[1]
        last_day_of_last_month = lastMonth.replace(day=split)
        ##############3
        student_search_obj = student_obj.search([('admission_date', '<=', last_day_of_last_month), ('admission_date', '>=', lastMonth)])  # 33333333#############   write first afterwords
        if student_search_obj:
            for student in student_search_obj:
                student_prgramme = student.programme
                if student_prgramme:
                    if student_prgramme == "Integrated":
                        integrated_list.append(student_prgramme)
                        integrated_name.append(student.name)
                    if student_prgramme == "MID":
                        mid_list.append(student_prgramme)
                        mid_name.append(student.name)
                    if student_prgramme == "ASD":
                        asd_list.append(student_prgramme)
                        asd_name.append(student.name)
            student_programme_obj = student_obj.search([('last_change_programme', '<=', last_day_of_last_month), ('last_change_programme', '>=', lastMonth)])
            for student in student_programme_obj:
                prgramme = student.programme
                if prgramme:
                    if prgramme == "Integrated":
                        if prgramme not in integrated_list:
                            integrated_list.append(student_prgramme)
            student_withdraw_obj = student_obj.search([('withdraw_date', '>=', first), ('withdraw_date', '<=', last_day_selected_month_date)])
            for student in student_withdraw_obj:
                student_withdraw_prgramme = student.programme
                if student_withdraw_prgramme:
                    if student_withdraw_prgramme == "Integrated":
                        withdraw_integrated_list.append(student_withdraw_prgramme)
                        integrated_withdraw_name.append(student.name)
                    if student_withdraw_prgramme == "MID":
                        withdraw_mid_list.append(student_withdraw_prgramme)
                        mid_withdraw_name.append(student.name)
                    if student_withdraw_prgramme == "ASD":
                        withdraw_asd_list.append(student_withdraw_prgramme)
                        asd_withdraw_name.append(student.name)
            name_int = ",".join(str(x) for x in integrated_name)
            name_asd = ",".join(str(x) for x in asd_name)
            name_mid = ",".join(str(x) for x in mid_name)
            
            withdraw_name_int = ",".join(str(x) for x in integrated_withdraw_name)
            withdraw_name_asd = ",".join(str(x) for x in asd_withdraw_name)
            withdraw_name_mid = ",".join(str(x) for x in mid_withdraw_name)
            
            programme_dict['Integrated'] = len(integrated_list)
            programme_dict['MID'] = len(mid_list)
            programme_dict['ASD'] = len(asd_list)
            programme_dict['withdraw_Integrated'] = len(withdraw_integrated_list)
            programme_dict['withdraw_MID'] = len(withdraw_mid_list)
            programme_dict['withdraw_ASD'] = len(withdraw_asd_list)
            programme_dict['withdraw_total'] = len(withdraw_integrated_list) + len(withdraw_mid_list) + len(withdraw_asd_list)
            programme_dict['I_Name'] = name_int
            programme_dict['A_Name'] = name_asd
            programme_dict['M_Name'] = name_mid
            programme_dict['withdraw_integrated_Name'] = withdraw_name_int
            programme_dict['withdraw_asd_Name'] = withdraw_name_asd
            programme_dict['withdraw_mid_Name'] = withdraw_name_mid
            programme_dict['Total'] = len(integrated_list) + len(mid_list) + len(asd_list)
            return programme_dict
        else:
            return programme_dict

    @api.multi
    def render_html(self, docids, data=None):
#        data.update({'date_selection': self.env['monthly.enrolment.wizard'].date_selection}) # self.env['monthly.enrolment.wizard'].context
        date_selection = data['form'].get('date_selection')
        integrated_dict = {}
        self.model = self.env.context.get('active_model')
        docs = self.env['student.student'].browse(self.env.context.get('active_ids', []))
        student_obj = self.env['student.student']
        student_search_obj = student_obj.search([('state_custom', '=', 'draft')])
        model = self.env.context.get('active_model')
        enrolment_year, enrolment_month, year_list , integrated_dict , mid_dict , asd_dict = self._age_ids(date_selection) 
        total_programme = self._total_no()
        programme_dict = self._total_admitted_student_previous_month(date_selection)
        mylist = mid_dict['MID']
        myintegrated = integrated_dict['Integrated']
        myasd = asd_dict['ASD']
        mydic = {}
        myintegrated_dict = {}
        myasd_dict = {}
        for dic in mylist:
            for key, value in dic.items():
                if key in mydic:
                    mydic[key].append(value)
                else:
                    mydic[key] = [value]
        for dic in myintegrated:
            for key, value in dic.items():
                if key in myintegrated_dict:
                    myintegrated_dict[key].append(value)
                else:
                    myintegrated_dict[key] = [value]
        for dic in myasd:
            for key, value in dic.items():
                if key in myasd_dict:
                    myasd_dict[key].append(value)
                else:
                    myasd_dict[key] = [value]
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model or 'student.student',
            'docs': self.env['student.student'].browse(1),
            'year_list':year_list,
            'integrated_dict':myintegrated_dict,
            'mid_dict':mydic,
            'asd_dict':myasd_dict,
            'programme_dict':total_programme,
            'enrolment_year':enrolment_year,
            'enrolment_month':enrolment_month,
            'programme_dict2':programme_dict
        }
        return self.env['report'].render('atts_student_fields.report_studentdetail', docargs)
