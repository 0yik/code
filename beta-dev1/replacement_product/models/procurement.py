# -*- coding: utf-8 -*-

from odoo import api, fields, models, registry, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.picking_ids:
            self.picking_ids.do_unreserve()
            self.picking_ids.move_lines.write({'state': 'draft'})
        return res

SaleOrder()