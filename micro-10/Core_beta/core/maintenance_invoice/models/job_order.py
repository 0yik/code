# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from datetime import  datetime

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    maintenance_request_id = fields.Many2one('maintenance.request')

class InvoiceableCharges(models.Model):
    _name = 'invoice.charge'

    product_id = fields.Many2one('product.product', required=1, string='Product')
    name = fields.Char('Description',required=1, related='product_id.name')
    qty = fields.Integer('Quantity',required=1, default=1)
    unit_price = fields.Float('Unit Price',required=1,related='product_id.lst_price')
    total = fields.Float('Total', compute='compute_total')
    job_order_id = fields.Many2one('job.order')
    maintenance_request_id = fields.Many2one('maintenance.request', related=False)

    @api.depends('unit_price','qty')
    @api.multi
    def compute_total(self):
        for rec in self:
            if rec.qty and rec.unit_price:
                rec.total = rec.qty * rec.unit_price

    @api.model
    def create(self,vals):
        if 'job_order_id' in vals:
            job_order = self.env['job.order'].browse(vals['job_order_id'])
            if job_order.maintenance_id:
                vals.update(
                    {
                        'maintenance_request_id' : job_order.maintenance_id.id
                    }
                )
        return super(InvoiceableCharges, self).create(vals)

class JobOrder(models.Model):
    _inherit = 'job.order'

    invoiceable_charges_ids = fields.One2many('invoice.charge','job_order_id')

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    invoice_count = fields.Integer('#Invoice', compute='compute_invoice_count')
    invoiceable_charges_ids = fields.One2many('invoice.charge', 'maintenance_request_id')
    check_is_invoice_open = fields.Boolean('Check Invoice is open ?', defaul=False, compute='compute_check_is_invoice_open')
    invoice_ids = fields.One2many('account.invoice', 'maintenance_request_id')

    @api.depends('invoice_ids')
    @api.multi
    def compute_check_is_invoice_open(self):
        for rec in self:
            if rec.invoice_ids:
                if all([re.state  in ['draft','cancel'] for re in rec.invoice_ids]):
                    rec.check_is_invoice_open = False
                else:
                    rec.check_is_invoice_open = True

    def action_create_invoice(self):
        exist_invoice = self.env['account.invoice'].search([('maintenance_request_id','=',self.id)])
        if exist_invoice:
            exist_invoice.unlink()
        journal = self.env['account.journal'].search([('type','=','sale')], limit=1)
        invoice_val = {
            'partner_id': self.customer_id and self.customer_id.id or False,
            'account_id': self.customer_id and self.customer_id.property_account_receivable_id and self.customer_id.property_account_receivable_id.id or False,
            'journal_id': journal and journal.id or False,
            'company_id': self.customer_id and self.customer_id.company_id and self.customer_id.company_id.id or False ,
            'currency_id': self.customer_id and self.customer_id.company_id and self.customer_id.company_id.currency_id.id or False,
            'date_invoice': datetime.now().date(),
            'maintenance_request_id' : self.id,
            'type': 'out_invoice',
            'user_id' : self.technician_user_id and self.technician_user_id.id or False,
        }
        invoice = self.env['account.invoice'].create(invoice_val)
        for invoice_line in self.invoiceable_charges_ids:
                line_val = {
                    'name' : invoice_line.name,
                    'invoice_id': invoice.id,
                    'uom_id' : invoice_line.product_id.uom_id and invoice_line.product_id.uom_id.id or False,
                    'product_id': invoice_line.product_id.id,
                    'account_id': self.customer_id and self.customer_id.property_account_receivable_id and self.customer_id.property_account_receivable_id.id or False,
                    'price_unit': invoice_line.unit_price,
                    'quantity': invoice_line.qty,
                }
                self.env['account.invoice.line'].create(line_val)
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'res_id': invoice.id
        }

    @api.depends('invoice_ids')
    @api.multi
    def compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.invoice_ids)


    @api.multi
    def action_view_invoice(self):
        return {
             'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_ids[0].id
        }