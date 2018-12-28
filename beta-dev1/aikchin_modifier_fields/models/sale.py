# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    location_id = fields.Many2one('stock.location', 'Location', copy=False)
    cost_price = fields.Float('Cost Price')

class DeliveryAddress(models.Model):
    _inherit = 'delivery.address'

    @api.multi
    def name_get(self):
        res = []
        for partner in self:
            full_address = [partner.street, partner.street2, partner.city, partner.state_id.name, partner.country_id.name, partner.zip]
            address = [x for x in full_address if x]
            res.append((partner.id, ', '.join(address)))
        return res

        # address = []
        # res = []
        # for partner in self:
        #     street = partner.street or ''
        #     street2 = partner.street2 or ''
        #     city = partner.city or ''
        #     zip = partner.zip or ''
        #     state = partner.state_id.name or ''
        #     country = partner.country_id.name or ''
        #     if street != '' and street != 'False':
        #         address.append(street)
        #     if street2 != '' and street2 != 'False':
        #         address.append(street2)
        #     if city != '' and city != 'False':
        #         address.append(city)
        #     if zip != '' and zip != 'False':
        #         address.append(zip)
        #     if country != '' and country != 'False':
        #         address.append(country)
        #     if state != '' and state != 'False':
        #         address.append(state)
        #     partner_addr = ", ".join(address)
        #     res.append((partner.id, partner_addr))
        # return res

class sales_order(models.Model):
    _inherit = 'sale.order'

    customer_po = fields.Char(string='Customer PO')
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='amount')
    project_id= fields.Many2one('account.analytic.account' , required=True)
    def get_default_issue(self):
        issuer = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        return issuer.id

    supp_id = fields.Many2one('hr.employee', 'Issuerss', default=get_default_issue)
    invoice_address = fields.Char('Invoice Address', required=True)

    @api.model
    def default_get(self, fields):
        res = super(sales_order, self).default_get(fields=fields)
        issuer = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        res['issuer_id'] = issuer.id
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(sales_order, self).onchange_partner_id()
        if self.partner_id:
            payment_term_id = self.partner_id.property_payment_term_ids.ids
            full_address = [self.partner_id.street, self.partner_id.street2, self.partner_id.city, self.partner_id.state_id.name, self.partner_id.country_id.name, self.partner_id.zip]
            address = [x for x in full_address if x]
            self.invoice_address = ', '.join(address)
            self.payment_term_id = payment_term_id[0] if payment_term_id else None
            delivery_addr = self.partner_id.delivery_address_ids.ids
            self.partner_delivery_address_id = delivery_addr[0] if delivery_addr else None

            return { 'domain' : {
                        'partner_delivery_address_id': [('id', 'in', delivery_addr)],
                        'payment_term_id': [('id', 'in', payment_term_id)],
                        }
                    }

    def action_confirm(self):
        res = super(sales_order, self).action_confirm()
        self.state = 'sale'
        return res

    @api.model
    def create(self,vals):
        res = super(sales_order, self).create(vals)
        if res.partner_id and 'invoice_address' not in vals:
            full_address = [res.partner_id.street, res.partner_id.street2, res.partner_id.city,
                            res.partner_id.state_id.name, res.partner_id.country_id.name, res.partner_id.zip]
            address = [x for x in full_address if x]
            res.invoice_address = ', '.join(address)
        return res

    @api.multi
    def write(self,vals):
        if 'partner_id' in vals and 'invoice_address' not in vals:
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            full_address = [partner_id.street, partner_id.street2, partner_id.city,
                            partner_id.state_id.name, partner_id.country_id.name, partner_id.zip]
            address = [x for x in full_address if x]
            vals.update({
                'invoice_address' : ', '.join(address),
            })
        res = super(sales_order, self).write(vals)
        return res
