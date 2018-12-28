# -*- encoding: utf-8 -*-
from odoo import api, fields, models
# import ipywidgets as widgets

# from openerp import netsvc,api
# from openerp.exceptions import ValidationError
# from openerp.osv.orm import browse_record_list, browse_record, browse_null
# from openerp.tools.translate import _

class terms_condition(models.Model):
    _name= 'tc.module'

    name = fields.Char('Name')
    terms = fields.Text(string='Terms & Condtions')
    active = fields.Boolean('Active', default=True)
    sale_ord = fields.Boolean('Sale Order & Quotations')
    purchase_ord = fields.Boolean('Purchase RFQ & Purchase Orders')
    accnt_ord = fields.Boolean('Invoices')

class sale_order(models.Model):
    _inherit ='sale.order'

    term_tmpl_id = fields.Many2one('tc.module', 'T&C')

    @api.onchange('term_tmpl_id')
    def onchange_term_tmpl_id(self):
        note = self.term_tmpl_id.terms
        return {'value':{'note': note}}

class purchase_order(models.Model):
    _inherit ='purchase.order'

    term_tmpl_id = fields.Many2one('tc.module', 'T&C')

    @api.onchange('term_tmpl_id')
    def onchange_term_tmpl_id(self):
        note = self.term_tmpl_id.terms
        return {'value': {'notes': note}}

class account_invoice(models.Model):
    _inherit ='account.invoice'

    term_tmpl_id = fields.Many2one('tc.module', 'T&C')

    @api.onchange('term_tmpl_id')
    def onchange_term_tmpl_id(self):
        note = self.term_tmpl_id.terms
        return {'value': {'comment': note}}