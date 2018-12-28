# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    number_of_days = fields.Integer(string="Number of days to calculate")
    reorder_buffer = fields.Float(string="Reorder buffer (%)")

    @api.multi
    def set_number_of_days(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default('purchase.config.settings', 'number_of_days', config.number_of_days)

    @api.multi
    def set_reorder_buffer(self):
        check = self.env.user.has_group('base.group_system')
        Values = check and self.env['ir.values'].sudo() or self.env['ir.values']
        for config in self:
            Values.set_default('purchase.config.settings', 'reorder_buffer', config.reorder_buffer)