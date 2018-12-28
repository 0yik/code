# -*- coding: utf-8 -*-

import time
from datetime import datetime
import xlwt
from xlsxwriter.workbook import Workbook
from cStringIO import StringIO
import base64
from PIL import Image
from odoo import api, fields, models

class sales_pipeline_wizard(models.TransientModel):
    _name ='sales.pipeline.wizard'
    
    country_id = fields.Many2one('res.country','Country')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    
    def print_pipeline_excel(self):
        crm_lead_pool = self.env['crm.lead']
        crm_lead_ids = crm_lead_pool.search([('country_id','=',self.country_id.id),('type','=','opportunity'), ('create_date','>=',self.start_date),('create_date','<=',self.end_date)])
        filename = 'Pipelines.csv'
        workbook = xlwt.Workbook()
        
        xlwt.add_palette_colour("custom_colour", 0x21)
        workbook.set_colour_RGB(0x21, 0, 96, 168)
        xlwt.add_palette_colour("custom_colour1", 0x22)
        workbook.set_colour_RGB(0x22, 155, 194, 230)
        xlwt.add_palette_colour("custom_colour2", 0x23)
        workbook.set_colour_RGB(0x23, 47, 117, 181)
        xlwt.add_palette_colour("custom_colour3", 0x24)
        workbook.set_colour_RGB(0x24, 0, 176, 240)
        
        style1 = xlwt.easyxf('pattern: pattern solid, fore_color custom_colour; font: bold True; font: name Times New Roman; font: color white; font:height 400; align: horiz center; borders: top double, bottom double, left double, right double;')
        style2 = xlwt.easyxf('pattern: pattern solid, fore_color custom_colour1; font: bold True; font: name Times New Roman; font:height 250; align: horiz center; borders: top double, bottom double, left double, right double;')        
        style3 = xlwt.easyxf('pattern: pattern solid, fore_color custom_colour2; font: bold True; font: name Times New Roman; font:height 250; borders: top double, bottom double, left double, right double;')
        style4 = xlwt.easyxf('pattern: pattern solid, fore_color custom_colour3; font: bold True; font: name Times New Roman; font:height 250; borders: top double, bottom double, left double, right double;')
        style5 = xlwt.easyxf('borders: top double, bottom double, left double, right double;')
        
        
        worksheet = workbook.add_sheet('Sheet 1')
        worksheet.row(0).height = 256*2
        worksheet.write_merge(0,0,0,8,'Financial Solutions - Sales Pipeline (Corporate)',style1)
        
        end_date_list = self.end_date.split('-')
        first_date_year = end_date_list[0]+'-'+'01'+'-'+'01'+' '+'00:00:00'
        worksheet.row(1).height = 350*1
        worksheet.write(1,0, self.country_id.name, style2)
        worksheet.write(1,1, 'Start Date', style2)
        worksheet.write(1,2, self.start_date, style2)
        worksheet.write(1,3, 'End Date', style2)
        worksheet.write(1,4, self.end_date , style2)
        worksheet.write(1,5, '', style2)
        worksheet.write(1,6, '', style2)
        worksheet.write(1,7, '', style2)
        worksheet.write(1,8, '', style2)
        
        worksheet.write(2,0, 'Company', style3)
        worksheet.write(2,1, 'Country', style3)
        worksheet.write(2,2, 'Account Manager', style3)
        worksheet.write(2,3, 'Services/Solutions', style3)
        worksheet.write(2,4, 'Potential Revenue  Monthly', style3)
        worksheet.write(2,5, 'Potential Revenue Annual', style3)
        worksheet.write(2,6, 'Start Date/Billing', style3)
        worksheet.write(2,7, 'Probability', style3)
        worksheet.write(2,8, 'Remarks', style3)
        
        
        row = 3
        total_monthly_revunue = 0
        total_yearly_revunue = 0
        currency = False
        for lead in crm_lead_ids:
            currency = lead.company_currency
            yearly_revunue = 0
            if lead.partner_id:
                worksheet.write(row,0,lead.partner_id.name,style5)
                lead_ids = crm_lead_pool.search([('country_id','=',self.country_id.id),('partner_id','=',lead.partner_id.id),('type','=','opportunity'), ('create_date','>=',first_date_year),('create_date','<=',self.end_date)])
                for lead_id in lead_ids:
                    yearly_revunue += lead_id.planned_revenue
            else:
                worksheet.write(row,0,'',style5)
            if lead.country_id:
                worksheet.write(row,1,lead.country_id.name,style5)
            else:
                worksheet.write(row,1,'',style5)
            if lead.user_id:
                worksheet.write(row,2,lead.user_id.name,style5)
            else:
                worksheet.write(row,2,'',style5)
            if lead.name:
                worksheet.write(row,3,lead.name,style5)
            else:
                worksheet.write(row,3,'',style5)
            total_yearly_revunue += yearly_revunue
            if lead.planned_revenue:
                worksheet.write(row,4,lead.planned_revenue,style5)
            else:
                worksheet.write(row,4,'',style5)
            
            worksheet.write(row,5,yearly_revunue,style5)
            
            if lead.start_date:
                worksheet.write(row,6,lead.start_date,style5)
            else:
                worksheet.write(row,6,'',style5)
            if lead.probability:
                worksheet.write(row,7,lead.probability,style5)
            else:
                worksheet.write(row,7,'',style5)
            if lead.description:
                worksheet.write(row,8,lead.description,style5)
            else:
                worksheet.write(row,8,'',style5)
            total_monthly_revunue += lead.planned_revenue
            row += 1
        
        worksheet.row(row).height = 350*1
        worksheet.write(row,0,'Total Monthly Revenue',style4)
        worksheet.write(row,1,'',style4)
        worksheet.write(row,2,'',style4)
        if currency != False: 
            worksheet.write(row,3,currency.name,style4)
        else:
            worksheet.write(row,3,'',style4)
        worksheet.write(row,4,total_monthly_revunue,style4)
        worksheet.write(row,5,'',style4)
        worksheet.write(row,6,'',style4)
        worksheet.write(row,7,'',style4)
        worksheet.write(row,8,'',style4)
        worksheet.row(row+1).height = 350*1
        worksheet.write(row+1,0,'Total Potential Yearly Revenue',style4)
        worksheet.write(row+1,1,'',style4)
        worksheet.write(row+1,2,'',style4)
        if currency != False:
            worksheet.write(row+1,3,currency.name,style4)
        else:
            worksheet.write(row+1,3,'',style4)
        worksheet.write(row+1,4,'',style4)
        worksheet.write(row+1,5,total_yearly_revunue,style4)
        worksheet.write(row+1,6,'',style4)
        worksheet.write(row+1,7,'',style4)
        worksheet.write(row+1,8,'',style4)
        fp = StringIO()
        workbook.save(fp)
        export_id = self.env['sales.pipeline.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        return {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'sales.pipeline.excel',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self._context,
                'target': 'new',
        }
     

class sales_pipeline_excel(models.TransientModel):
    _name= "sales.pipeline.excel"
     
    excel_file = fields.Binary('Excel file for Sales Pipeline')
    file_name = fields.Char('Excel File', size=64)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
