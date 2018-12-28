# -*- coding: utf-8 -*-

from odoo import fields, models, api

class Partner(models.Model):
    _inherit = "res.partner"
	
    def _default_country(self):
        country = self.env['res.country'].search([('code', '=', 'SG')])
        if country:
               return country

    supplier_id = fields.Char(string="Supplier ID")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_default_country)
    property_payment_term_ids = fields.Many2many('account.payment.term', string='Customer Payment Terms')
    property_supplier_payment_term_ids = fields.Many2many('account.payment.term', string='Vendor Payment Terms')
    #issuer_id = fields.Many2one('hr.employee', 'Issuer')

    @api.multi
    def update_delivery_address(selt):
        customer_ids = selt.env['res.partner'].search(['|',('customer','=',True),('supplier','=',True)])
        fla = 0
        for customer_id in customer_ids:
            if not customer_id.delivery_address_ids and fla != 100:
                fla += 1
                customer_id.delivery_address_ids += customer_id.delivery_address_ids.new({
                    'street' : customer_id.street,
                    'street2' : customer_id.street2,
                    'city'    : customer_id.city,
                    'state_id' : customer_id.state_id,
                    'zip'      : customer_id.zip,
                    'country_id'  : customer_id.country_id
                })

class year_config_inherit(models.Model):
    _inherit = 'year.config'

    @api.model
    def create(self,vals):
        res = super(year_config_inherit, self).create(vals)
        res.on_change_year()
        return res

    @api.multi
    def write(self,vals):
        res = super(year_config_inherit, self).write(vals)
        if 'year' in vals:
            self.on_change_year()
        return res