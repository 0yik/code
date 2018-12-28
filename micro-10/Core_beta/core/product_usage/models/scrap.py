# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
        scrap = super(models.Model, self).create(vals)
        return scrap