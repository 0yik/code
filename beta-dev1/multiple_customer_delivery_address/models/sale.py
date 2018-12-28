# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.partner_id and self.partner_id.delivery_address_ids.ids:
            vals = {}
            value = {}
            delivery_addr = self.partner_id.delivery_address_ids.ids
            vals['domain'] = {'partner_delivery_address_id': [('id', 'in', delivery_addr)]}
            value['partner_delivery_address_id'] = delivery_addr[0]
            self.update(value)
            return vals

    partner_delivery_address_id = fields.Many2one('delivery.address', string='Delivery Address', readonly=True, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order.")
    partner_related_delivery_ids = fields.One2many('delivery.address', string='Delivery Address', related="partner_id.delivery_address_ids")
