from odoo import models, fields, api

class inventory_adjustment(models.Model):
    _inherit ='stock.inventory'

class inventory_adjustment_line(models.Model):
    _inherit = 'stock.inventory.line'

    missed_item = fields.Float(string="Differentiate",compute='_compute_missed_item')
    missed_checkbox = fields.Boolean('Missed Item',default=True)

    @api.depends('theoretical_qty', 'product_qty')
    def _compute_missed_item(self):
        for rec in self:
            rec.missed_item = rec.product_qty - rec.theoretical_qty