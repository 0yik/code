# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeliveryAddress(models.Model):
    _name = 'delivery.address'
    _rec_name = 'country_id'

    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'SG')])
        if country:
            return country
        return False

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='Zip', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_default_country)
    partner_id = fields.Many2one('res.partner', string='Partner')
    contact = fields.Char('Contact')
    
    @api.model
    def create(self,vals):
        if 'partner_id' in self._context:
            vals.update({
                'partner_id' : self._context.get('partner_id'),
            })
        return super(DeliveryAddress, self).create(vals)

    @api.multi
    def name_get(self):

        res = []
        for partner in self:
            address = []
            street = partner.street or ''
            street2 = partner.street2 or ''
            city = partner.city or ''
            zip = partner.zip or ''
            state = partner.state_id.name or ''
            country = partner.country_id.name or ''
            if street != '' and street != 'False':
                address.append(street)
            if street2 != '' and street2 != 'False':
                address.append(street2)
            if city != '' and city != 'False':
                address.append(city)
            if zip != '' and zip != 'False':
                address.append(zip)
            if state != '' and state != 'False':
                address.append(state)
            if country != '' and country != 'False':
                address.append(country)
            partner_addr = ", ".join(address)
            res.append((partner.id, partner_addr))
        return res
