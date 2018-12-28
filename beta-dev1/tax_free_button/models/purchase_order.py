# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _check_tax_free_button(self):
        tax_free_button = self.env['ir.values'].get_default('purchase.config.settings',
                                                                 'tax_free_button')
        self.check_tax_free_button = tax_free_button

    check_tax_free_button = fields.Boolean(compute=_check_tax_free_button)

    @api.multi
    def tax_free_button(self):
        for record in self:
            if record.order_line.mapped('taxes_id'):
                for line in record.order_line:
                    line.taxes_id = None
            else:
                for line in record.order_line:
                    line.taxes_id = line.product_id.supplier_taxes_id


class purchase_config_settings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    tax_free_button = fields.Boolean(string="Apply Tax Free Button")

    @api.model
    def get_default_tax_free_button(self, fields):
        return {
            'tax_free_button': self.env['ir.values'].get_default('purchase.config.settings',
                                                                 'tax_free_button')
        }

    @api.multi
    def set_default_tax_free_button(self):
        IrValues = self.env['ir.values']
        IrValues.set_default('purchase.config.settings', 'tax_free_button', self.tax_free_button)