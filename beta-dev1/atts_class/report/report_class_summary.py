#-*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from odoo import api, fields, models


class ReportClassSummary(models.AbstractModel):
    _name = 'report.atts_class.report_class_summary'

    def get_data_am(self):
        data_class_am = []
        class_obj = self.env['class.class']
        act_domain = [('session','=','am')]
        class_ids = class_obj.search(act_domain)
        am_total_male=0
        am_total_female=0
        am_total = 0
        for data in class_ids:
            male = 0
            female=0
            total=0
            for student in self.env['class.student.list'].search([('class_id','=',data.id)]):
                if student.student_id.gender=='male':
                    male = male+1
                if student.student_id.gender=='female':
                    female = female+1
                total=male+female
            am_total_female = am_total_female+female
            am_total_male = am_total_male+male
            am_total = am_total+total
            data_class_am.append({'name': data.name,
                               'room_no': data.room_no.name,
                               'teacher': data.class_teacher_id.name,
                               'male':male,
                               'female':female,
                               'total':total,
                               })
        return data_class_am, am_total_male, am_total_female, am_total
    def get_data_pm(self):
        data_class_pm = []
        class_obj = self.env['class.class']
        act_domain = [('session','=','pm')]
        class_ids = class_obj.search(act_domain)
        pm_total_male=0
        pm_total_female=0
        pm_total = 0
        for data in class_ids:
            male = 0
            female=0
            total=0
            for student in self.env['class.student.list'].search([('class_id','=',data.id)]):
                if student.student_id.gender=='male':
                    male = male+1
                if student.student_id.gender=='female':
                    female = female+1
                total=male+female
            pm_total_female = pm_total_female+female
            pm_total_male = pm_total_male+male
            pm_total = pm_total+total
            data_class_pm.append({'name': data.name,
                               'room_no': data.room_no.name,
                               'teacher': data.class_teacher_id.name,
                               'male':male,
                               'female':female,
                               'total':total,
                               })
        return data_class_pm, pm_total_male, pm_total_female, pm_total

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        data_res_am,am_total_male,am_total_female,am_total= self.get_data_am()
        data_res_pm,pm_total_male,pm_total_female,pm_total = self.get_data_pm()
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'class_data_am': data_res_am,
            'class_data_pm': data_res_pm,
            'pm_total_male' : pm_total_male,
            'pm_total_female':pm_total_female,
            'pm_total':pm_total,
            'am_total_male' : am_total_male,
            'am_total_female':am_total_female,
            'am_total':am_total,
            }
        render_model = 'atts_class.report_class_summary'
        return self.env['report'].render(render_model, docargs)
