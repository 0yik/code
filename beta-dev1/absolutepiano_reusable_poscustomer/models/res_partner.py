# -*- coding: utf-8 -*-

from odoo import models, fields, api


class partner_country_code(models.Model):
    _name = 'partner.country.code'
    _order = "name desc"

    name = fields.Char('Code', required=True)
    country = fields.Many2one('res.country', 'Country', required=True)
    country_name = fields.Char(related='country.name')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name or '/'
            if record.country and record.country.name:
                name = name + ' (%s)'%(record.country.name)
            res.append((record.id, name))
        return res

    @api.onchange('country')
    @api.one
    def onchange_country(self):
        if self.country and self.country.id and self.country.phone_code:
            self.name = '+' + str(self.country.phone_code)

    @api.model
    def prepare_all_country_code(self):
        countries = self.env['res.country']
        for country in countries.search([]):
            if not self.search([('country','=',country.id)]) and country.phone_code:
                self.create({
                    'name' : '+' + str(country.phone_code),
                    'country' : country.id,
                })

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_default_country_code(self):
        singapore = self.env.ref('base.sg')
        code = self.env['partner.country.code'].search([('country','=',singapore.id)],limit=1)
        return code.id or False

    @api.depends('country_code', 'company_mobile')
    @api.one
    def compute_country_code_mobile(self):
        code = self.country_code.name or ''
        mobile = self.company_mobile or ''
        self.mobile = code + mobile

    unit_no = fields.Char('Unit No.')

    use_delivery_addr = fields.Boolean('Delivery Address')
    d_unit_no = fields.Char('Delivery Unit No.')
    d_street = fields.Char('Delivery Street')
    d_city = fields.Char('Delivery City')
    d_zip = fields.Char('Delivery Zip')
    d_country_id = fields.Many2one('res.country', 'Delivery Country')

    company_mobile = fields.Char('Mobile')
    country_code = fields.Many2one('partner.country.code', 'Country Code', default=_get_default_country_code)
    mobile = fields.Char('Mobile', compute=compute_country_code_mobile)