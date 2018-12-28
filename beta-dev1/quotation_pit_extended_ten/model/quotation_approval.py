# -*- coding: utf-8 -*-
from odoo.osv.orm import setup_modifiers
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

class sign_line(models.Model):
	_name = 'sign.line'

	user_id = fields.Many2one('res.users','User')
	signature = fields.Binary('Signature')
	filename = fields.Char('filename')
	company_id = fields.Many2one('res.company','Company')

class res_company(models.Model):
	_inherit = 'res.company'

	sign_line_ids = fields.One2many('sign.line','company_id','Sign Line')

	def get_approved_image(self, obje, company):
		sign_obj = self.env['sign.line'].search([('user_id','=',obje.approved_by.id)])
		return sign_obj.signature

	def get_approved(self, obje):
		sign_obj = self.env['sign.line'].search([('user_id','=',obje.approved_by.id)])
		return sign_obj.user_id.name

class sale_order(models.Model):
	_inherit = 'sale.order'

	approved_by = fields.Many2one('res.users','User')
	state = fields.Selection([
	    ('draft', 'Quotation'),
	    ('sent', 'Quotation Sent'),
	    ('waiting_approval','Waiting For Approval'),
	    ('approved','Approved'),
	    ('sale', 'Sales Order'),
	    ('done', 'Locked'),
	    ('cancel', 'Cancelled'),
	    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	def approv_quotation_send(self):
		recipient_list = []
		for sale in self:
			if self.company_id.sign_line_ids:
				for user in self.company_id.sign_line_ids:
					recipient_list.append(user.user_id.partner_id.id)
			action_id = self.env['ir.model.data'].get_object_reference('sale','action_quotations')[1]
			menu_id = self.env['ir.model.data'].get_object_reference('sale','menu_sale_quotations')[1]
			template = self.env.ref('quotation_pit_extended_ten.email_template_sale_order_approval_report', False).with_context({'action_id':action_id,'menu_id':menu_id})
			mail_id = template.send_mail(self.id,recipient_list)
			self.env['mail.mail'].browse(mail_id).send()
			sale.write({'state':'waiting_approval'})

