
# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import time
from datetime import datetime
from odoo import models, api
from datetime import date

    

class ReportFeeOutstanding(models.AbstractModel):
    _name = 'report.school_fees.outstanding_fee_report'


    def get_data(self):
        data_report = []
        count= 0
        register_obj = self.env['student.fees.register']
        self._cr.execute("truncate table outstanding_report")
        cur_date = date.today().strftime('%Y-%m-%d')
        for student in self.env['student.student'].search([]):
            self._cr.execute("insert into outstanding_report (student_id,student_name,class_no) values(%s,%s,%s)",(student.id,student.name,student.class_level+student.class_number));
            self._cr.execute('update outstanding_report set six_grt=0');
        for data in register_obj.search([],order='date DESC'):
            due_date = datetime.strptime(data.date, '%Y-%m-%d').date()
            cur_date1 = datetime.strptime(cur_date, '%Y-%m-%d').date()
            no_days = (cur_date1 - due_date).days + 1
            if no_days>0 and no_days<31:
                one_mth=0
                for line in self.env['register.student.list'].search([('register_id','=',data.id)]):
                    one_mth = line.total-line.amount_paid
                    self._cr.execute('update outstanding_report set one_mth=%s where student_id=%s',(one_mth,line.student_id.id));
                    self._cr.commit();
            if no_days>30 and no_days<61:
                two_mth=0
                for line in self.env['register.student.list'].search([('register_id','=',data.id)]):
                    two_mth = line.total-line.amount_paid
                    self._cr.execute('update outstanding_report set two_mth=%s where student_id=%s',(two_mth,line.student_id.id));
                    self._cr.commit();
            if no_days>60 and no_days<91:
                three_mth=0
                for line in self.env['register.student.list'].search([('register_id','=',data.id)]):
                    three_mth = line.total-line.amount_paid
                    self._cr.execute('update outstanding_report set three_mth=%s where student_id=%s',(three_mth,line.student_id.id));
                    self._cr.commit();
            if no_days>90 and no_days<121:
                four_mth=0
                for line in self.env['register.student.list'].search([('register_id','=',data.id)]):
                    four_mth = line.total-line.amount_paid
                    self._cr.execute('update outstanding_report set four_mth=%s where student_id=%s',(four_mth,line.student_id.id));
                    self._cr.commit();
            if no_days>120 and no_days<151:
                five_mth=0
                for line in self.env['register.student.list'].search([('register_id','=',data.id)]):
                    five_mth = line.total-line.amount_paid
                    self._cr.execute('update outstanding_report set five_mth=%s where student_id=%s',(five_mth,line.student_id.id));
                    self._cr.commit();
            if no_days>150 and no_days<181:
                six_mth=0
                for line in self.env['register.student.list'].search([('register_id','=',data.id)]):
                    six_mth = line.total-line.amount_paid
                    self._cr.execute('update outstanding_report set six_mth=%s where student_id=%s',(six_mth,line.student_id.id));
                    self._cr.commit();
            if no_days>181:
                for line in self.env['register.student.list'].search([('register_id','=',data.id)]):
                    six_mth_grt = (line.total-line.amount_paid)
                    self._cr.execute('select six_grt from outstanding_report where student_id=%s'%line.student_id.id);
                    c1 = self._cr.fetchall()
                    list1 = [int(i[0]) for i in c1]
                    
                    self._cr.execute('update outstanding_report set six_grt=%s where student_id=%s',(six_mth_grt+list1[0],line.student_id.id));
                    self._cr.commit();
        total=0
        for report_data in self.env['outstanding.report'].search([],order='class_no ASC'):
            total=report_data.one_mth+report_data.two_mth+report_data.three_mth+report_data.four_mth+report_data.five_mth+report_data.six_mth+report_data.six_grt
            if total>0:
                data_report.append({
                                     'name': report_data.student_name,
                                     'class':report_data.class_no,
                                     '1_mth':report_data.one_mth,
                                     '2_mth':report_data.two_mth,
                                     '3_mth':report_data.three_mth,
                                     '4_mth':report_data.four_mth,
                                     '5_mth':report_data.five_mth,
                                     '6_mth':report_data.six_mth,
                                     '6_mth_grt':report_data.six_grt,
                                     'total':report_data.one_mth+report_data.two_mth+report_data.three_mth+report_data.four_mth+report_data.five_mth+report_data.six_mth+report_data.six_grt,
                                     })
        return data_report
    
    def get_total(self):
        data_total = []
        sum_one_mth=sum_two_mth=sum_three_mth=sum_four_mth=sum_five_mth=sum_six_mth=sum_six_grt=total=0
        for report_data in self.env['outstanding.report'].search([]):
            sum_one_mth += report_data.one_mth
            sum_two_mth += report_data.two_mth
            sum_three_mth += report_data.three_mth
            sum_four_mth += report_data.four_mth
            sum_five_mth += report_data.five_mth
            sum_six_mth += report_data.six_mth
            sum_six_grt += report_data.six_grt
        total=sum_one_mth+sum_two_mth+sum_three_mth+sum_four_mth+sum_five_mth+sum_six_mth+sum_six_grt
        data_total.append({
                             '1_mth':sum_one_mth,
                             '2_mth':sum_two_mth,
                             '3_mth':sum_three_mth,
                             '4_mth':sum_four_mth,
                             '5_mth':sum_five_mth,
                             '6_mth':sum_six_mth,
                             '6_mth_grt':sum_six_grt,
                             'total':sum_one_mth+sum_two_mth+sum_three_mth+sum_four_mth+sum_five_mth+sum_six_mth+sum_six_grt,
                             })
        return data_total,total
            
        
    

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        res_data = self.get_data()
        res_data1,total = self.get_total()
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'data_report': res_data,
            'data_total': res_data1,
            'total':total,
            }
        render_model = 'school_fees.outstanding_fee_report'
        return self.env['report'].render(render_model, docargs)