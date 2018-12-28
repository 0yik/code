#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from odoo.osv import osv
from odoo import models, fields, api, tools
from odoo.tools.translate import _
import StringIO
import base64
import xlrd
import string
import sys
from odoo.exceptions import UserError, ValidationError


class items_import(models.TransientModel):
      
    _name ="items.import"
  
    datas = fields.Binary('Data')
    datas_fname = fields.Char('Filename',size=256)
    
    @api.multi
    @api.model
    def import_data(self):
        ''' Import the Attendance Records.
            Create a new record if EMP ID, Year and Monthnot found in the application.
            Writes the record if found.
        '''
        curr_obj = self  
        if not curr_obj.datas:
            raise UserError(_('Please Choose The File!'))
        file_name = curr_obj.datas_fname
        fname = str(file_name.split('.')[1])
        if fname != 'xls':
            raise UserError(_('Please Choose The File With .xls extension and proper format!'))
        try:
            val=base64.decodestring(curr_obj.datas)
            fp = StringIO.StringIO()
            fp.write(val)     
            wb = xlrd.open_workbook(file_contents=fp.getvalue())
            wb.sheet_names()
            sheet_name=wb.sheet_names()
            sh = wb.sheet_by_index(0)
            sh = wb.sheet_by_name(sheet_name[0])
            n_rows = sh.nrows
        except:
            raise ValidationError("File format not supported!")    
        emp_pool = self.env['hr.employee']
        year_pool = self.env['hr.year']
        attendance_pool = self.env['hr.attendance']
        year_dic = {}
        count = 0
	row = 0
        for r in range(1, n_rows):
            val= {}
            if not sh.row_values(r)[0]:
                raise UserError("No Employee Code found in the sheet at row '"+str(r)+"'.")
            code = sh.row_values(r)[0]
            if isinstance(code,float):
                emp_id = str(int(code))
            else:
                try:
                    emp_id = str(sh.row_values(r)[0]).strip()
                except UnicodeError as e:
                    emp_id = sh.row_values(r)[0].strip()
            value = sh.row_values(r)[2]
            if isinstance(value,float):
                    raise ValidationError('May you have choosen wrong file or given wrong data. Please check once')
            emp_obj = emp_pool.search([('emp_id','=',emp_id)], limit=1, order="id desc") or False
            if emp_obj:
                val['employee_code'] = emp_id
                val['employee_id'] = emp_obj.id
                val['department_id'] = emp_obj.department_id.id
                val['late_cnts'] = sh.row_values(r)[3]
                val['early_cnts'] = sh.row_values(r)[4] 
                val['rest'] = sh.row_values(r)[5]
                val['ph'] = sh.row_values(r)[6]
                val['late_hrs'] = sh.row_values(r)[7]
                val['early_hrs'] = sh.row_values(r)[8]
                val['tot_brk_hrs'] = sh.row_values(r)[9]
                val['absents'] = sh.row_values(r)[10]
                val['dedn'] = sh.row_values(r)[11]
                val['half_days'] = sh.row_values(r)[12]
                val['total_abs'] = sh.row_values(r)[13]
                val['ot'] = sh.row_values(r)[14]
                val['month'] = sh.row_values(r)[15]
                if sh.row_values(r)[15] not in ['JAN','FEB','MAR','APR','JUN','JUL','MAY','AUG','SEP','OCT','NOV','DEC']:
                    raise ValidationError("Format of the Month column should be in ('JAN','FEB','MAR','APR','JUN','JUL','MAY','AUG','SEP','OCT','NOV','DEC')")		
                year_val = sh.row_values(r)[16]
                if type(year_val) is float and str(year_val).split('.')[1] == "0":
                    year = str(year_val).split('.')[0]
                else: 
                    try:
                        year = str(year_val)
                    except UnicodeError as e:
                        year = year_val
                if year:
                    if year in year_dic.keys():
                        year_obj = year_dic[year]
                    else:
                        year_obj =  year_pool.search([('name','=',year)]) or False
                        year_dic.update({year:year_obj})
                    if not year_obj:
                        raise UserError("Year '"+year+"' not found in the Year master. Please create the year.")
                    val['year'] = year_obj.id
                attend_obj = attendance_pool.search([('employee_id','=',emp_obj.id),('month','=',val['month']),('year','=',val['year'])], limit=1, order="id desc") or False
                val['no_validation'] = True
                if attend_obj:
                    attend_obj.write(val)
                else:
                    attendance_pool.create(val)
                count += 1
                if count == 5:
                    self.env.cr.commit()
                    count = 0
                    
            elif not emp_obj:
		raise ValidationError("No Employee found with given data row '"+str(r)+"'.")
	    row += 1
	view_id = self.env['ir.model.data'].get_object_reference('employee_appraisal','import_success_view_form')[1]	
	if row == n_rows-1:
	    self.env.cr.commit()
	    raise ValidationError("Import Done Successfully!")       
