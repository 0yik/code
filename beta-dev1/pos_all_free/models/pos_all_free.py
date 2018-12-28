# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit= "pos.order"

    all_free = fields.Boolean('Apply All Free?')
    
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['all_free'] = ui_order.get('all_free')
        return res