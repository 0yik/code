# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_order_line(models.Model):
    _inherit= 'sale.order.line'

    @api.model
    def default_get(self, fields):
        res = super(sale_order_line, self).default_get(fields)
        tag_id = self.env['account.analytic.tag'].search([('name','=','Sales')],limit=1)
        if tag_id:
            res['analytic_tag_ids'] = [(4,tag_id.id)]
        return res
