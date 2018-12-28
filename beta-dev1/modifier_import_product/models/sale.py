# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    code = fields.Char(string='Product Code')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        self.update({'code':self.product_id.product_tmpl_id.code})
        return res

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def create(self, vals):
        procurement = super(ProcurementOrder, self.with_context(tracking_disable=True)).create(vals)
        if not self._context.get('tracking_disable'):
            procurement.run()
        return procurement

    @api.multi
    def write(self, vals):
        procurement = super(ProcurementOrder, self.with_context(tracking_disable=True)).write(vals)
        return procurement
