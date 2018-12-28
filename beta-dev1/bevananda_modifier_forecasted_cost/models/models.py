# -*- coding: utf-8 -*-

from odoo import models, fields, api

class bevananda_modifier_forecasted_cost(models.Model):
    _name = 'forcasted.cost'

    types = fields.Char(string="Type",required=True)
    name = fields.Char(string="Cost Type",required=True)

class bevananda_modifier_forecasted_cost(models.Model):
    _name = 'forcasted.cost.line'
    cost_element=fields.Many2one('product.product',string="Cost Element")
    cost_vendor=fields.Many2one('res.partner',string="Cost Vendor")
    cost_amount = fields.Char(string="Product Cost")
    cost_type=fields.Many2one('forcasted.cost',string="Cost Type")
    reimbursable = fields.Boolean(string="Reimbursable")
    sale_id=fields.Many2one('sale.order')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    forcasted_cost_line=fields.One2many('forcasted.cost.line','sale_id',string="Forcasted Cost")