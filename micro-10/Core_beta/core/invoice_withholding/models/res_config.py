# -*- coding: utf-8 -*-

from odoo import fields, models, api
import werkzeug.urls


class ResCompany(models.Model):
    _inherit = "res.company"

    withholding_product_id = fields.Many2one('product.product', string='Withholding Product')
    withholding_percentage = fields.Float(string='Withholding Percentage')


class ResConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    withholding_product_id = fields.Many2one('product.product', string='Withholding Product')
    withholding_percentage = fields.Float(string='Withholding Percentage')

    @api.model
    def get_default_withholding(self, fields):
        return {
            'withholding_product_id': self.env.user.company_id.withholding_product_id and self.env.user.company_id.withholding_product_id.id or False,
            'withholding_percentage': self.env.user.company_id.withholding_percentage
        }

    @api.multi
    def set_invoice_withholding(self):
        self.ensure_one()
        if not self.env.user._is_admin():
            raise AccessError(_("Only administrators can change the settings"))

        self.env.user.company_id.withholding_product_id = self.withholding_product_id.id
        self.env.user.company_id.withholding_percentage = self.withholding_percentage


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: