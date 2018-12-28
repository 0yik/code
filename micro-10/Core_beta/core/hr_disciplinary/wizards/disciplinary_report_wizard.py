import xlsxwriter
import datetime
from time import gmtime, strftime

# from xlwt import Book
from odoo import models, fields, api

class DisciplinaryReportWizard(models.TransientModel):
	_name = 'disciplinary.report.wizard'

	all_employee = fields.Boolean()
	all_stages = fields.Boolean()
	from_date = fields.Date(required=True)
	to_date = fields.Date(required=True)
	employee = fields.Many2one('hr.employee', string="Employee", required=True)
	disciplinary_stages = fields.Many2one('disciplinary.stage', string="Disciplinary Stages", required=True)

	@api.multi
	def save(self):
		company = self.env.user.company_id
		datetime.datetime.now()
		workbook = xlsxwriter.Workbook('sheet8.xlsx')
		c_time = strftime("%Y-%m-%d", gmtime())
		import pdb; pdb.set_trace()
		worksheet = workbook.add_worksheet()
		bold = workbook.add_format({'bold': True})
		worksheet.write(0,3, company.name, bold)
		worksheet.write(2,0, 'Title', bold)
		worksheet.write(2,1, 'Disciplinary Report', bold)
		worksheet.write(3,0, 'Company Name', bold)
		worksheet.write(3,1, company.name, bold)
		worksheet.write(4,0, 'Date', bold)
		worksheet.write(4,1, c_time, bold)
		worksheet.write(7,0, 'Annual Leave', bold)
		worksheet.write(9,0, 'Department', bold)
		worksheet.write(9,1, 'Employee ID', bold)
		worksheet.write(9,2, 'Employee Name', bold)
		worksheet.write(9,3, 'Disciplined Date', bold)
		worksheet.write(9,4, 'Disciplinary Stages', bold)
		worksheet.write(9,5, 'Valid Until', bold)
		worksheet.write(9,6, 'Reason of Disciplinary', bold)
		worksheet.write(10,2, 'Administrator', bold)