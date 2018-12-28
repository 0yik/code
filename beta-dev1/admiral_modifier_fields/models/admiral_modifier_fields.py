# -*- coding: utf-8 -*-

from odoo import models, fields, api

class admiral_modifier(models.Model):
    _inherit = "product.template"

    appearance      = fields.Text('Appearance')
    colour          = fields.Text('Colour')
    ol_des_top      = fields.Text('Olfactory Description Top')
    ol_des_body     = fields.Text('Olfactory Description Body')
    ol_des_bottom   = fields.Text('Olfactory Description Bottom')
    odour           = fields.Text('Odour')
    density         = fields.Text('Density')
    refrac_index    = fields.Text('Refraction Index at 25 Degree')
    acid_value      = fields.Text('Acid Value')
    purity          = fields.Text('Purity')
    shelf_life      = fields.Text('Shelf Life')
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    deli_term = fields.Text('Delivery Terms')