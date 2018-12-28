#-*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from odoo import api, fields, models


class ReportClassGroup(models.AbstractModel):
    _name = 'report.atts_class.report_class_group'

    def get_data_kindness(self):
        data_level = []
        level_obj = self.env['level.level']
        act_domain = [('end_date','=', False)]
        level_ids = level_obj.search(act_domain)
        for data in level_ids:
            if data.subject=='english':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['english.level.history'].search([('level_name','=',data.name),('end_date','=',False),('english_level_number','=',str(num))]):
                        if student.student_id.class_level=='kindness':
                            count=len(student)+count  
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                   })
            if data.subject=='math':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['math.level.history'].search([('level_name','=',data.name),('end_date','=',False),('math_level_number','=',str(num))]):
                        if student.student_id.class_level=='kindness':
                            count=len(student)+count           
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                      })
        return data_level
    def get_data_love(self):
        data_level = []
        level_obj = self.env['level.level']
        act_domain = [('end_date','=', False)]
        level_ids = level_obj.search(act_domain)
        for data in level_ids:
            if data.subject=='english':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['english.level.history'].search([('level_name','=',data.name),('end_date','=',False),('english_level_number','=',str(num))]):
                        if student.student_id.class_level=='love':
                            count=len(student)+count  
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                   })
            if data.subject=='math':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['math.level.history'].search([('level_name','=',data.name),('end_date','=',False),('math_level_number','=',str(num))]):
                        if student.student_id.class_level=='love':
                            count=len(student)+count           
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                      })
        return data_level
    def get_data_hope(self):
        data_level = []
        level_obj = self.env['level.level']
        act_domain = [('end_date','=', False)]
        level_ids = level_obj.search(act_domain)
        for data in level_ids:
            if data.subject=='english':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['english.level.history'].search([('level_name','=',data.name),('end_date','=',False),('english_level_number','=',str(num))]):
                        if student.student_id.class_level=='hope':
                            count=len(student)+count  
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                   })
            if data.subject=='math':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['math.level.history'].search([('level_name','=',data.name),('end_date','=',False),('math_level_number','=',str(num))]):
                        if student.student_id.class_level=='hope':
                            count=len(student)+count           
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                      })
        return data_level
    def get_data_joy(self):
        data_level = []
        level_obj = self.env['level.level']
        act_domain = [('end_date','=', False)]
        level_ids = level_obj.search(act_domain)
        for data in level_ids:
            if data.subject=='english':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['english.level.history'].search([('level_name','=',data.name),('end_date','=',False),('english_level_number','=',str(num))]):
                        if student.student_id.class_level=='joy':
                            count=len(student)+count  
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                   })
            if data.subject=='math':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['math.level.history'].search([('level_name','=',data.name),('end_date','=',False),('math_level_number','=',str(num))]):
                        if student.student_id.class_level=='joy':
                            count=len(student)+count           
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                      })
        return data_level
    def get_data_peace(self):
        data_level = []
        level_obj = self.env['level.level']
        act_domain = [('end_date','=', False)]
        level_ids = level_obj.search(act_domain)
        for data in level_ids:
            if data.subject=='english':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['english.level.history'].search([('level_name','=',data.name),('end_date','=',False),('english_level_number','=',str(num))]):
                        if student.student_id.class_level=='peace':
                            count=len(student)+count  
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                   })
            if data.subject=='math':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['math.level.history'].search([('level_name','=',data.name),('end_date','=',False),('math_level_number','=',str(num))]):
                        if student.student_id.class_level=='peace':
                            count=len(student)+count           
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                      })
        return data_level
    def get_data_victory(self):
        data_level = []
        level_obj = self.env['level.level']
        act_domain = [('end_date','=', False)]
        level_ids = level_obj.search(act_domain)
        for data in level_ids:
            if data.subject=='english':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['english.level.history'].search([('level_name','=',data.name),('end_date','=',False),('english_level_number','=',str(num))]):
                        if student.student_id.class_level=='victory':
                            count=len(student)+count  
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                   })
            if data.subject=='math':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['math.level.history'].search([('level_name','=',data.name),('end_date','=',False),('math_level_number','=',str(num))]):
                        if student.student_id.class_level=='victory':
                            count=len(student)+count           
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                      })
        return data_level
    def get_data_glory(self):
        data_level = []
        level_obj = self.env['level.level']
        act_domain = [('end_date','=', False)]
        level_ids = level_obj.search(act_domain)
        for data in level_ids:
            if data.subject=='english':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['english.level.history'].search([('level_name','=',data.name),('end_date','=',False),('english_level_number','=',str(num))]):
                        if student.student_id.class_level=='glory':
                            count=len(student)+count  
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                   })
            if data.subject=='math':
                num=0
                no_levels=int(data.no_levels)
                while num<no_levels:
                    num=num+1
                    count=0
                    for student in self.env['math.level.history'].search([('level_name','=',data.name),('end_date','=',False),('math_level_number','=',str(num))]):
                        if student.student_id.class_level=='glory':
                            count=len(student)+count           
                    data_level.append({'name': data.name,
                                       'number':num,
                                       'no_student':count,
                                      })
        return data_level
    

    @api.model
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        data_res_kindness = self.get_data_kindness()
        data_res_love = self.get_data_love()
        data_res_joy = self.get_data_joy()
        data_res_hope = self.get_data_hope()
        data_res_peace = self.get_data_peace()
        data_res_victory = self.get_data_victory()
        data_res_glory = self.get_data_glory()
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'level_data_kindness': data_res_kindness,
            'level_data_joy': data_res_joy,
            'level_data_hope': data_res_hope,
            'level_data_peace': data_res_peace,
            'level_data_victory': data_res_victory,
            'level_data_glory': data_res_glory,
            'level_data_love': data_res_love,
            }
        render_model = 'atts_class.report_class_group'
        return self.env['report'].render(render_model, docargs)
