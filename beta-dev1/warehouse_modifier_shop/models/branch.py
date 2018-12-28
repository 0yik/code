# -*- coding: utf-8 -*-
from odoo import models, fields, api

class res_branch(models.Model):
    _inherit = 'res.branch'

    company_id = fields.Many2one('res.company', string='Company', required=False)
    is_warehouse = fields.Boolean('Is A Warehouse')

    @api.model
    def create(self, vals):
        warehouse_vals = {}
        if vals.get('is_warehouse') and not self.env.context.get('from_location'):
            warehouse_vals['name'] = vals.get('name')
            warehouse_vals['code'] = vals.get('country_code','')
            warehouse_vals['is_shop'] = True
            self.env['stock.warehouse'].with_context({'from_branch': True}).create(warehouse_vals)
        return super(res_branch, self).create(vals)

res_branch()