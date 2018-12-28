# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

import base64
import StringIO
import xlsxwriter
import csv
import os.path

class res_partner(models.Model):
	_inherit = 'res.partner'

	@api.model
	def create(self, vals):
		w = super(res_partner,self).create(vals)
		if w.company_type == 'company':
			sale_pricelist_id = self.env['product.pricelist'].create({
				'name':str(w.short_name) + '_' + str(w.partner_code),
				'item_ids': [(0, 0, {
						'applied_on': '3_global',
						'compute_price': 'fixed',
						'fixed_price': 0.0,
					})]
			})
			value = {
				'property_product_pricelist':sale_pricelist_id.id,
			}
			w.write(value)
		return w

class sale_order_send(models.TransientModel):
	_name = 'sale.order.send'

	email_to = fields.Char('Email')

	@api.one
	def approv_sale_send(self):
		w = self
		template = self.env.ref('quotation_pit_extended_ten.email_template_sale_order_approval_send', False).with_context({'email_to':w.email_to})
		mail_id = template.send_mail(self._context.get('active_id'))
		self.env['mail.mail'].browse(mail_id).send()
		self.env['sale.order'].browse(self._context.get('active_id')).write({'state':'sent'})
		return True

class sale_order_approval(models.TransientModel):
	_name = 'sale.order.approval'

	def _get_data(self):
		userlist= []
		company_obj = self.env['sale.order'].browse(self._context.get('active_id')).company_id
		if company_obj and company_obj.sign_line_ids:
			for i in company_obj.sign_line_ids:
				userlist.append(i.user_id.id)
		return [('id', 'in', userlist)]

	approved_by = fields.Many2one('res.users','User', domain=_get_data)

	@api.one
	def approv_sale(self):
		if self._context.get('active_id'):
			w = self
			sale_obje = self.env['sale.order'].browse(self._context.get('active_id'))
			sale_obje.write({'state':'approved','approved_by':w.approved_by.id})
		return True

class crm_askcode_partner(models.TransientModel):
	_name = 'crm.askcode.partner'
	_description = 'Lead To Partner'


	short_name = fields.Char('Short Name', required=True)
	code_partner = fields.Char('Code',required=True)
	acc_type = fields.Selection(string='Account Type',selection=[('local','Local'), ('international', 'International')],default="local")

	@api.onchange('acc_type')
	def onchange_acc_type(self):
		for partner in self:
			if self._context.get('active_id'):
				lead_obje = self.env['crm.lead'].browse(self._context.get('active_id'))
				if self.acc_type == 'local':
					self.code_partner = str(1130)+ '/' + str(lead_obje.comp_name[:1])
				else:
					self.code_partner = str(1137)+ '/' + str(lead_obje.comp_name[:1])

	@api.v7
	def convert_to_part(self,context=None):
		if context.get('active_id'):
			w = self
			lead_obje = self.env['crm.lead'].browse(context.get('active_id'))
			partner = self.env['res.partner']
			vals_dict = {}
			if lead_obje.comp_name:

				contact_dict = {
					'partner_code': w.code_partner + '/CON',
					'short_name':w.short_name,
					'acc_type':w.acc_type,
					'name':lead_obje.name,
					'title':lead_obje.title.id,
					'function':lead_obje.function,
					'user_id': self._uid,
					'email':lead_obje.email_from,
					'mobile':lead_obje.mobile,
					'is_company': False,
					'company_type':'person',
					'type': 'contact',
					'customer':True,
					'supplier':False,
				}
				vals_dict = {
					'partner_code': w.code_partner,
					'short_name':w.short_name,
					'acc_type':w.acc_type,
					'child_ids':[(0,0,contact_dict)],
					'name':lead_obje.comp_name,
					'phone':lead_obje.phone,
					'user_id': self._uid,
					'partner_code':w.code_partner,
					'street':lead_obje.street,
					'street2':lead_obje.street2,
					'city':lead_obje.city,
					'state_id':lead_obje.state_id.id,
					'website':lead_obje.website,
					'fax':lead_obje.fax,
					'country_id':lead_obje.country_id.id,
					'zip':lead_obje.zip,
					'is_company': True,
					'company_type':'company',
					'type': 'contact',
					'customer':True,
					'supplier':False,
				}
				partner_id = partner.create(vals_dict)
				lead_obje.unlink()
				models_data = self.env['ir.model.data']

				# Get opportunity views
				dummy, form_view = models_data.get_object_reference('base', 'view_partner_form')
				dummy, tree_view = models_data.get_object_reference('base', 'view_partner_tree')
				return {
					'name': _('Accounts'),
					'view_type': 'form',
					'view_mode': 'tree, form',
					'res_model': 'res.partner',
					'res_id': int(partner_id),
					'view_id': False,
					'views': [(form_view or False, 'form'),
							  (tree_view or False, 'tree'),],
					'type': 'ir.actions.act_window',
					'context': {}
				}


class crm_askcode_ponumber(models.TransientModel):
	_name = 'crm.askcode.ponumber'

	po_num = fields.Char('PO Number', required=True)
	order_date = fields.Date('Order Date', required=True)

	@api.one
	def confirm_sale(self):
		self.with_context({'po_num':self.po_num})
		context = self.env.context.copy()
		context.update({'po_num':self.po_num,'order_date':self.order_date})
		new_order = self.env['sale.order'].browse(self._context.get('active_id')).with_context(context).action_confirm()
		print ">>>>>>>>",new_order
		models_data = self.env['ir.model.data']
		# Get opportunity views
		dummy, form_view = models_data.get_object_reference('sale', 'view_order_form')
		dummy, tree_view = models_data.get_object_reference('sale', 'view_order_tree')
		return {
			'name': _('Sale Order'),
			'view_type': 'form',
			'view_mode': 'tree, form',
			'res_model': 'sale.order',
			'res_id': int(new_order.id),
			'view_id': False,
			'views': [(form_view or False, 'form'),
					  (tree_view or False, 'tree'),],
			'type': 'ir.actions.act_window',
			'context': {}
		}


class coating_date_wizard(models.TransientModel):
	_name = 'coating.date.wizard'

	coating_en = fields.Many2one('coating.enquiry','Coating')
	start_date = fields.Date('Start Date', required=True)
	end_date = fields.Date('End Date',required=True)


	@api.multi
	def get_report(self):
		res = self
		output =  StringIO.StringIO()
		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
		worksheet = workbook.add_worksheet()
		row = 1
		col = 0
		bold_format = workbook.add_format({'bold':  1})
		right_format = workbook.add_format({'bold':1,'align':'right'})
		merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter'})
		worksheet.merge_range('A1:H2', 'Coating Report     From Date : ' + datetime.strptime(self.start_date, '%Y-%m-%d').strftime('%m/%d/%Y')  + " To : " + datetime.strptime(self.end_date, '%Y-%m-%d').strftime('%m/%d/%Y') , merge_format)
		worksheet.set_column(row, col, 20)
		row +=2
		worksheet.write(row, col, 'Sr No.', bold_format)
		worksheet.set_column(row, col, 20)
		col += 1

		worksheet.write(row, col, 'SO NO', bold_format)
		worksheet.set_column(row, col, 20)
		col += 1

		worksheet.write(row, col, 'Product', bold_format)
		worksheet.set_column(row, col, 20)
		col += 1

		worksheet.write(row, col, 'Coating', bold_format)
		worksheet.set_column(row, col, 20)
		col += 1

		worksheet.write(row, col, 'Qty', bold_format)
		worksheet.set_column(row, col, 20)
		col += 1

		worksheet.write(row, col, 'Unit Price', bold_format)
		worksheet.set_column(row, col, 20)
		col += 1

		worksheet.write(row, col, 'Summary', bold_format)
		worksheet.set_column(row, col, 20)
		col += 1

		
		worksheet.write(row, col, 'Total Amount', bold_format)
		worksheet.set_column(row, col, 20)
		col += 1

		row = 4
		count =1
		row +=1
		for lead in res.get_order_line(self):
			row += 1
			col = 0
			worksheet.write(row, col,count or '')
			count += 1
			col += 1

			worksheet.write(row, col,lead.order_id.name or '')
			col += 1
			
			worksheet.write(row, col,lead.product_id.name or '')
			col += 1

			worksheet.write(row, col,lead.coating_en.name or '')
			col += 1

			worksheet.write(row, col,str(lead.product_uom_qty) + ' ' + str(lead.product_uom.name) or '')
			col += 1

			worksheet.write(row, col,lead.price_unit or '')
			col += 1

			worksheet.write(row, col,lead.name or '')
			col += 1

			worksheet.write(row, col,lead.price_subtotal or 0.0)
			col += 1
		row += 2
		row += 1

		worksheet.write(row, 6, 'Total', bold_format)
		worksheet.set_column(row, col, 20)
		worksheet.write(row, 7,str(res.get_total(self)['currency_id'].name) + ' ' + str(res.get_total(self)['total']) or 0.0,right_format)

		workbook.close()
		output.seek(0)
		result = base64.b64encode(output.read())
		attachment_obj = self.env['ir.attachment']
		attachment_id = attachment_obj.create({'name': 'Part Code.xlsx', 'datas_fname': 'Part Code.xlsx', 'datas': result})
		download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
		base_url = self.env['ir.config_parameter'].get_param('web.base.url')

		return {
			"type": "ir.actions.act_url",
			"url": str(base_url) + str(download_url),
			"target": "self",
		}

	@api.multi
	def get_total(self, obj):
		sale_obj = self.env['sale.order'].search([('state','=','sale'),('confirmation_date','>=',obj.start_date),('confirmation_date','<=',obj.end_date)])
		list_of_line = 0.0
		if sale_obj:
			for order in sale_obj:
				for line in order.order_line:
					if obj.coating_en:
						if line.coating_en.id == obj.coating_en.id:
							list_of_line += line.price_subtotal
					else:
						if line.coating_en.id:
							list_of_line += line.price_subtotal
						
		final_dict = {
			'currency_id':self.env.user.company_id.currency_id,
			'total':list_of_line
		}
		return final_dict		

	@api.multi
	def get_order_line(self,obj):
		sale_obj = self.env['sale.order'].search([('state','=','sale'),('confirmation_date','>=',obj.start_date),('confirmation_date','<=',obj.end_date)])
		list_of_line = []
		if sale_obj:
			for order in sale_obj:
				for line in order.order_line:
					if obj.coating_en:
						if line.coating_en.id == obj.coating_en.id:
							list_of_line.append(line)
					else:
						if line.coating_en.id:
							list_of_line.append(line)

		return list_of_line

	@api.multi
	def confirm_print(self):
		datas = {
			'ids': [],
			'model': 'sale.order',
			'date_start': self.start_date,
			'date_stop': self.end_date
		}
		return self.env['report'].get_action([], 'quotation_pit_extended_ten.coating_report_template', data=datas)
