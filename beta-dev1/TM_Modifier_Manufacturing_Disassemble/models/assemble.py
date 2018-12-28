# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockProductionLot(models.Model):
    _inherit = 'assemble.materials'

    attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Attributes',
        help="BOM Product Variants needed form apply this line.", related='product_id.attribute_value_ids')

    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     if self.product_id:
    #         return {
    #             'domain':{
    #                 'attribute_value_ids' : [('id','in',self.product_id.attribute_value_ids.ids)]
    #             }
    #         }
    #     return {
    #         'domain': {
    #             'attribute_value_ids': [('id', 'in', [])]
    #         }
    #     }
StockProductionLot()

class Res_Assemble(models.Model):
    _inherit = 'res.assemble'

    total_cost = fields.Float('Cost', compute='compute_cost')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=False)

    @api.model
    def create(self, vals):
        result = super(Res_Assemble, self).create(vals)
        if result.product_id:
            result.product_id.standard_price = result.total_cost
        return result

    @api.multi
    def write(self, vals):
        result = super(Res_Assemble, self).write(vals)
        if self.product_id:
            self.product_id.standard_price = self.total_cost
        return result

    @api.multi
    @api.depends('material_id')
    def compute_cost(self):
        for rec in self:
            if rec.material_id:
                total = 0
                for line in rec.material_id:
                    if line.product_id.standard_price:
                        total = total + line.product_id.standard_price * line.qty_pro
                    else:
                        assemble = self.search([('product_id','=',line.product_id.product_tmpl_id.id)], limit=1)
                        if assemble:
                            total = total + assemble.total_cost/assemble.quantity_pro * line.qty_pro
                rec.total_cost = total

