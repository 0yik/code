# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    tc_template_id = fields.Many2one('sale.tc', string="Terms and Conditions Template")


    @api.onchange('tc_template_id')
    def _onchange_tc_template_id(self):
        if self.tc_template_id:
            self.comment = self.tc_template_id.terms
        else:
            self.comment = ''
    @api.model
    def create(self,vals):
        if not vals.get('tc_template_id'):
            tc_id = self.env.ref('modifier_ccm_pos_rental.standard_tnc').id
            vals.update({'tc_template_id':tc_id})
        return super(AccountInvoice,self).create(vals)

    inv_for = fields.Selection([('rental','Rental'),('sale','Sale')],string="Invoice Type")
    booking_end_date = fields.Date(string="End Date")
    
    def _get_refundable_deposit(self):
        for obj in self:
            obj.refundable_deposit = sum(obj.invoice_line_ids.filtered(lambda l:l.product_id.default_code == 'Advance').mapped('price_subtotal'))
            
    refundable_deposit = fields.Float(string="Refundbale Deposit",compute='_get_refundable_deposit')

    # send mail to customer with attached invoice
    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        order = self.env['pos.order'].search([('invoice_id', 'in', self.ids)])
        if order:
            template = self.env.ref('account.email_template_edi_invoice', False)
            if template and template.auto_delete:
                template.auto_delete = False
            ctx = dict(
                default_model='account.invoice',
                default_res_id=self.ids[0],
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_composition_mode='comment',
                mark_invoice_as_sent=True,
                custom_layout="account.mail_template_data_notification_email_account_invoice"
            )
            mail = template.with_context(ctx).send_mail(self.ids[0], force_send=True)
            order.write({'mail_status':self.env['mail.mail'].browse(mail).state})
        return res
