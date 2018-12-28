# -*- coding: utf-8 -*-

from odoo import api, models, _
import time
import collections
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from dateutil import parser
from datetime import datetime, date
# from pandas.tseries import offsets
from dateutil.relativedelta import relativedelta


class studentdetailwithdrawlreport(models.AbstractModel):
    _name = 'report.atts_student_fields.report_monthly_withdrawl'
    
    
    @api.multi
    def _monthly_withdrawl(self, date):
        student_dict = {}
        student_month_list = []
        student_year_list = []
        student_obj = self.env['student.student']
        selected_date = date
        split_date = selected_date.split('-')
        today = datetime.strptime(selected_date, DF).date()  # selected date converted to date   today - offsets.YearBegin().date() type(first)
        first = today.replace(day=1)  # 1st of selected month today.replace(ye=1)
        last_day_selected_month = calendar.monthrange(int(split_date[0]), int(split_date[1]))
        last_day_selected_month = last_day_selected_month[1]
        last_day_selected_month_date = first.replace(day=last_day_selected_month)
        year_bigin = today.replace(month=1, day=1)
        year_start = year_bigin
        year_end = today.replace(month=12, day=31)
        year_stop = year_end
        student_month_obj = student_obj.search([('state_custom','=','draft'),('admission_date', '>=', first),('admission_date', '<=', last_day_selected_month_date)])
        student_year_obj = student_obj.search([('state_custom','!=','draft'),('withdraw_date', '>=', year_start),('withdraw_date', '<=', year_stop)])
        if student_month_obj:
            for student_id in student_month_obj:
                student_month_list.append(student_id.id)
        if student_year_obj:
            for student_id in student_year_obj:
                student_year_list.append(student_id.id)
        if student_month_obj and student_year_obj:
            month = len(student_month_list)
            year = len(student_year_list)
            percent_year = year * 100
            dropout = percent_year / month
            student_dict['month'] = month
            student_dict['year'] = year
            student_dict['dropout'] = dropout
            return student_dict
        else:
            return student_dict
                
    
    @api.multi
    def render_html(self, docids, data=None):
        date_selection = data['form'].get('date_selection')
        self.model = self.env.context.get('active_model')
        model = self.env.context.get('active_model')
        student_dict = self._monthly_withdrawl(date_selection) 
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model or 'student.student',
            'docs': self.env['student.student'].browse(1),
            'student_dict':student_dict
        }
        return self.env['report'].render('atts_student_fields.report_monthly_withdrawl', docargs)

