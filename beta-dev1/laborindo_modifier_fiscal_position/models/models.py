# -*- coding: utf-8 -*-

from odoo import models, fields, api

class fiscal_position(models.Model):
    _inherit = 'account.fiscal.position'

    state_id = fields.Many2one('res.country.state', string='Federal States')

    @api.model
    def get_fiscal_position(self, partner_id, delivery_id=None):
        if partner_id:
            customer = self.env['res.partner'].browse(partner_id)
            fiscal_exist = self.env['account.fiscal.position'].search([
                ('state_id', '=', customer.state_id.id),
                ('zip_from', '<=', customer.zip),
                ('zip_to', '>=', customer.zip)
            ], limit=1)
            if fiscal_exist:
                return fiscal_exist.id
            else:
                return

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner_id = vals.get('partner_id')
            customer = self.env['res.partner'].browse(partner_id)
            fiscal_exist = self.env['account.fiscal.position'].search([
                ('state_id', '=', customer.state_id.id),
                ('zip_from', '<=',customer.zip),
                ('zip_to', '>=', customer.zip)
            ], limit=1)
            if fiscal_exist:
                vals.update({
                    'fiscal_position_id' : fiscal_exist.id
                })

        return super(sale_order, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('partner_id'):
            partner_id = vals.get('partner_id')
            customer = self.env['res.partner'].browse(partner_id)
            fiscal_exist = self.env['account.fiscal.position'].search([
                ('state_id', '=', customer.state_id.id),
                ('zip_from', '<=',customer.zip),
                ('zip_to', '>=', customer.zip)
            ], limit=1)
            if fiscal_exist:
                vals.update({
                    'fiscal_position_id' : fiscal_exist.id
                })
        return super(sale_order, self).write(vals)
    # zip_from
    # zip_to