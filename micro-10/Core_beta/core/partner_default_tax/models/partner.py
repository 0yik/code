# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        company_obj = self.env['res.company'].sudo().browse(self.env.user.company_id.id)
        res.update({'default_tax_ids': [(6, 0, company_obj.default_tax_ids.ids)]})
        return res

    default_tax_ids = fields.Many2many('account.tax', string='Default Tax')

ResPartner()