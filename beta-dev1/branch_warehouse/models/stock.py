# -*- coding: utf-8 -*-
from odoo import models, fields, api

class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_shop = fields.Boolean('Is A Shop')

stock_warehouse()


class stock_location_inherit(models.Model):
    _inherit = 'stock.location'

    is_shop = fields.Boolean('Is A Shop')
    branch_id = fields.Many2one('res.branch', string='Branch')

    @api.multi
    def write(self, vals):
        branch_vals = {}
        for record in self:
            warehouse_id = self.env['stock.warehouse'].search([('code', '=', record.location_id.name)])
            if vals.get('is_shop') and not record.branch_id and not self.env.context.get('from_branch'):
                branch_vals['name'] = warehouse_id.name
                branch_vals['country_code'] = record.location_id and record.location_id.name
                branch_vals['is_warehouse'] = True
                branch = self.env['res.branch'].with_context({'from_location': True}).create(branch_vals)
                vals['branch_id'] = branch.id
        return super(stock_location_inherit, self).write(vals)

stock_location_inherit()

class stock_warehouse_orderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    location_type = fields.Selection([('shop','Shop'),('warehouse','Warehouse')], default='shop', string='Type')

    @api.multi
    def onchange_location_type(self, location_type):
        if location_type == 'shop':
            domain = {'location_id': [('is_shop', '=', True)]}
        else:
            domain = {'location_id': [('is_shop', '=', False)]}
        return {'domain': domain}

stock_warehouse_orderpoint()

