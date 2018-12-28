from odoo import models, fields, api

class sale_order(models.Model):
    _inherit = 'sale.order'

    tax_term        = fields.Selection('get_tax_term',string='Tax Term',required=True,default='free')

    @api.model
    def get_tax_term(self):
        tax_term_list = []
        if self.partner_id:
            company_id = self.partner_id.company_id
        else:
            company_id = self.env.user.company_id
        tax_term_list.append(('company','Pay via %s'%(company_id.name)))
        tax_term_list.append(('customer','Pay via Customer'))
        tax_term_list.append(('free','Free tax'))
        return tax_term_list

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    payment_proof_name  = fields.Char('Payment Proof Name')
    payment_proof       = fields.Binary(string='Payment Proof')