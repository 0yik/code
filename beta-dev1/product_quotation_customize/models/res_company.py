# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResCompany(models.Model):
	_inherit = 'res.company'
	
	#reference = fields.Char('Reference')
	npwp_no = fields.Char('NPWP No')
	dom = fields.Char('Dom')
	#dok_no = fields.Char('DOK No')
	bank_acc_number = fields.Char('Bank Acc No')
	bank_bin = fields.Char('Bank Name')
	#enquiry_number = fields.Char('Enquiry Number')

