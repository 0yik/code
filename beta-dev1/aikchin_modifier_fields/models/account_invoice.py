# -*- coding: utf-8 -*-
import datetime
from odoo import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    location_id = fields.Many2one('stock.location', 'Location')

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    customer_po = fields.Char(string='Customer PO')
    date_invoice = fields.Date('Invoice Date', required=True,default=fields.Date.today)
    sales_order = fields.Char(string="Sales Order",compute='get_order_data')
    delivery_order = fields.Char(string='Delivery Order',compute='get_order_data')

    @api.model
    def get_order_data(self):
        sales_order_ids = self.env['sale.order'].search([])
        for sales_order in sales_order_ids:
            if self.id in sales_order.invoice_ids.ids:
                self.sales_order = sales_order.name
                if sales_order.mapped('picking_ids'):
                    self.delivery_order = sales_order.mapped('picking_ids')[0].name
                break

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        credit_note_id = self.env.ref('credit_debit_note.action_out_refund').id
        debit_note_id = self.env.ref('credit_debit_note.action_in_refund').id
        account = self.env.ref('account.action_invoice_tree1').id
	vendor = self.env.ref('account.action_invoice_tree2').id
        if self._context and 'params' in self._context and self._context['params']['action']:
            if view_type == 'tree' and credit_note_id == self._context['params']['action']:
                self.env.ref('aikchin_modifier_printouts.tax_invoice_report').name = 'Credit Note'
            if view_type == 'tree' and debit_note_id == self._context['params']['action']:
                self.env.ref('aikchin_modifier_printouts.tax_invoice_report').name = 'Debit Note'
            if view_type == 'tree' and account == self._context['params']['action']:
                self.env.ref('aikchin_modifier_printouts.tax_invoice_report').name = 'Tax Invoice'
	    if view_type == 'tree' and vendor == self._context['params']['action']:
                self.env.ref('aikchin_modifier_printouts.tax_invoice_report').name = 'Tax Invoice'

        result = super(account_invoice, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                          toolbar=toolbar, submenu=submenu)
        return result

class Location_inherit(models.Model):
    _inherit = "stock.location"

    @api.model
    def create(self,vals):
        company_action_id = self.env.ref('base.action_res_company_form').id
        vals_location_parent = {'location_id':vals.get('location_id')}
        vals.update({'location_id': False})
        res = super(Location_inherit, self).create(vals)
        if 'params' in self._context and self._context['params'].get('action') != company_action_id:
            res.location_id = vals_location_parent['location_id']
        if 'params' not in self._context or 'action' not in self._context['params']:
            res.location_id = vals_location_parent['location_id']
        return res





