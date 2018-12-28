# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    downpayment = fields.Selection([('fixed','Down Payment Fixed'),('percentage','Down Payment Percentage'),('invoice','Invoice')])
    
    # @api.depends('advance_payment_method')
    # def invoice_downpayment(self):
    # 	print "hiii-----------------"
    # 	print self

    @api.model
    def create(self, vals):
        if "advance_payment_method" in vals:
            res = super(account_invoice, self).create(vals)
            if vals['advance_payment_method'] != None:
            	print vals['advance_payment_method']
            	if vals['advance_payment_method'] == "fixed":
            		res.write({'downpayment':"fixed"})
            	if vals['advance_payment_method'] == "percentage":
            		res.write({'downpayment':"percentage"})
            	if not vals['advance_payment_method']:
            		res.write({'downpayment':"invoice"})    		
            return res
        else:
            res = super(account_invoice, self).create(vals)
            res.write({'downpayment':"invoice"})
            return res
                


class sale_order(models.Model):
    _inherit = 'sale.order'


    @api.multi
    def action_view_invoice(self):
        res = super(sale_order, self).action_view_invoice()        
        invoices = self.mapped('invoice_ids')
        if len(invoices) > 1:            
            res['context'] = {'group_by':'downpayment'}        
        return res

