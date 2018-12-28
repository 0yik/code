# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.osv import osv
from odoo.tools.translate import _
import math
import re
import StringIO
import cStringIO
import base64
import xlrd
import string
import sys
import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class employee_evaluation_import(models.TransientModel):
      
    _name ="employee.evaluation.import"
    datas = fields.Binary('Data')
    datas_fname = fields.Char('Filename',size=256)

    @api.multi
    @api.model
    def import_data(self):
        ''' Imports the Evaluation Records.
	    1) Creates the Rating records if not found.
	'''
        employee_evaluation_pool = self.env['employee.evaluation']
        rating_config_pool = self.env['rating.config']
        rating_values_pool = self.env['rating.values']
        employee_pool = self.env['hr.employee']
        job_pool = self.env['hr.job']
        year_config_pool = self.env['hr.year']
        department_pool = self.env['hr.department']
        quarter_line_pool = self.env['quarter.line']
        emp_rating_lines_pool = self.env['emp.rating.lines']
        quarter = ''        
        curr_obj = self  
        if not curr_obj.datas:
            raise UserError(_('Please Choose The File!'))
        file_name = curr_obj.datas_fname
        fname = str(file_name.split('.')[1])
        if fname != 'xls':
            raise UserError(_('Please choose the file with .xls extension and proper format!'))          
        val = base64.decodestring(curr_obj.datas)
        fp = StringIO.StringIO()
        fp.write(val)     
        wb = xlrd.open_workbook(file_contents=fp.getvalue())
        wb.sheet_names()
        sheet_name = wb.sheet_names()
        sh = wb.sheet_by_index(0)
        sh = wb.sheet_by_name(sheet_name[0])
        n_rows = sh.nrows
        count = 0
	row = 0
        emp_evaluation_data = {}
        for r in range(1, n_rows):            
            if len(sh.row_values(r))<4:
                raise UserError(_("Some data is missing in the row %s") % (str(r+1)))
            
            if not sh.row_values(r)[0]:
                raise UserError(_("Employee code/Id is empty in the row %s") % (str(r+1)))
            
            elif not sh.row_values(r)[1]:
                raise UserError(_("Employee Name is empty in the row %s") % (str(r+1)))
            else:
                code = sh.row_values(r)[0]
                if isinstance(code,float):
                    emp_code = str(int(code))
                else:
                    emp_code = str(sh.row_values(r)[0]).strip()
                emp_name = str(sh.row_values(r)[1]).strip()
                emp_id = employee_pool.search([('emp_id','=',emp_code),('name','=',emp_name)],limit=1) or False
                if not emp_id:
                    raise UserError(_("No employee found with Employee Id/Code(%s) and Name(%s)") % (emp_code, emp_name))                
                emp_evaluation_data['emp_id'] = emp_id.id
                emp_evaluation_data['employee_id'] = emp_id.emp_id
                emp_evaluation_data['department_id'] = emp_id.department_id and emp_id.department_id.id or False
                emp_evaluation_data['reviewer'] = emp_id.parent_id and emp_id.parent_id.id or False
                emp_evaluation_data['job_title'] = emp_id.job_id and emp_id.job_id.id or False            

            if not sh.row_values(r)[2]:
                raise UserError(_("Year is empty in the row %s") % (str(r+1)))
            else:
                val = sh.row_values(r)[2]
                if not isinstance(val,float):
                    raise ValidationError('May you have choosen wrong file or given the wrong data. Please check once')
                year = str(int(sh.row_values(r)[2])).strip()
                year_id = year_config_pool.search([('name','=', year)],limit=1) or False
                if not year_id:
                    raise UserError(_("Year %s is not found in the Year Master.") % (year))                
                emp_evaluation_data['year'] = year_id.id                

            if not sh.row_values(r)[3]:
                raise UserError(_("Quarter is empty in the row %s") % (str(r+1)))
            else:
                quarter = str(sh.row_values(r)[3]).lower().strip()
                emp_evaluation_data['quarter'] = quarter                        

            employee_evaluation_id = employee_evaluation_pool.search([('emp_id', '=', emp_id.id),('year','=', year_id.id), ('quarter','=', quarter)],limit=1) or False            
            name_list = []            
            rating_line = {}
            rating_line_list = []
            for data in [sh.row_values(r)[4:]]:
                for li in [data[i:i+3] for i in range(0, len(data), 3)]:
                    if len(li) == 3 and li[0] != '':                        
                        if '.0' in str(li[1]):
                            li[1] = str(int(li[1]))                             
                        else:
                            li[1] = str(li[1])
                        name_list.append(li[0])
                        rating_label_id = rating_config_pool.search([('name','=',li[0])], limit=1) or \
                                        rating_config_pool.create({'name':li[0], 'rating_ids': [(0,0,{'department_id': emp_id.department_id.id, 'score': li[1]})]})
                        rating_line['rating_label_id'] = rating_label_id.id 
                        if rating_label_id.name == 'Attendance':
                            rating_line['is_attendance_type'] = True
                        found = False
                        for obj in rating_label_id.rating_ids:
                            if obj.department_id.id == emp_id.department_id.id:
                                found = True
                                if obj.score != int(li[1]):                                    
				    raise ValidationError("At row number '"+str(r+1)+"', for rating label '"+li[0]+"' given rating value is not matching to rating configuration at respective department")
                        if not found:
                            rating_label_id.write({'rating_ids':[(0,0,{'department_id': emp_id.department_id.id, 'score': li[1]})]})
                        rating_val_id = rating_values_pool.search([('department_id','=', emp_id.department_id.id),('rating_id','=',rating_label_id.id),('name','=',li[1])], limit=1) or False
                        request.cr.execute("select min(name) from rating_values where department_id=%d and rating_id=%d"%(emp_id.department_id.id,rating_label_id.id))
                        value = request.cr.fetchone()
                        min_scr_obj = self.env['rating.values'].search([('name','=',value[0]),('department_id','=',emp_id.department_id.id),('rating_id','=',rating_label_id.id)], limit=1)
                        if not rating_val_id:
                            rate_line_id = False
                            for obj in rating_label_id.rating_ids:
                                if obj.department_id.id == emp_id.department_id.id:
                                    rate_line_id = obj.id
                                    rate_line_id = obj.id
				    if obj.score != int(li[1]):
                                        raise ValidationError("At row number '"+str(r+1)+"', for rating label '"+li[0]+"' given rating value is not matching to rating configuration at respective department")
                                    break;
                            rating_val_id = rating_values_pool.search([('department_id','=', emp_id.department_id.id),('rating_id','=',rating_label_id.id),('name','=',li[1])], limit=1) or False
                        rating_line['rating'] = min_scr_obj.id
                        rating_line['full_score'] = rating_val_id.id
                        rating_line['comment'] = li[2]                        
                        if employee_evaluation_id:
                            if employee_evaluation_id.status == 'draft':
                                emp_rating_line = emp_rating_lines_pool.search([('emp_rating_id', '=',employee_evaluation_id.id), ('rating_label_id', '=', rating_label_id.id)], limit=1) or False
                                if emp_rating_line:
                                    for obj in emp_rating_line:
                                        is_attendance_type = obj.rating_label_id.name == 'Attendance' and True or False
                                        obj.write({'rating': min_scr_obj.id,'full_score':rating_val_id.id,'comment': li[2], 'is_attendance_type':is_attendance_type})                          
                            else:
                                rating_line_list.append((0,0,rating_line))                            
                        else:
                            rating_line_list.append((0,0,rating_line))
                        rating_line = {}
            if employee_evaluation_id:   
                if employee_evaluation_id.status == 'draft':
                    employee_evaluation_id.write({'employee_id':emp_id.emp_id,'department_id':emp_id.department_id and emp_id.department_id.id or False,'reviewer':emp_id.parent_id and emp_id.parent_id.id or False ,'job_title':emp_id.job_id and emp_id.job_id.id or False,'emp_rating_ids': rating_line_list})

                    for line in employee_evaluation_id.emp_rating_ids:
                        if line.rating_label_id.name not in name_list:
                            employee_evaluation_id.write({'emp_rating_ids': [(2,line.id,0)] })
            else:
                emp_evaluation_data['emp_rating_ids'] = rating_line_list
		employee_evaluation_pool.create(emp_evaluation_data)	            
            count += 1
            if count == 20:
                self.env.cr.commit()
            count = 0
	    row += 1                         
	self.env.cr.commit()
        view_id = self.env['ir.model.data'].get_object_reference('employee_appraisal','import_success_view_form')[1]        
        if row == n_rows-1:            
	    self.env.cr.commit()
	    raise ValidationError("Import Done Successfully!")
               
        return True
