# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    code = fields.Char(string='Product Code')
    temp = fields.Boolean('Temp')
    
    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        self.update({'code':self.product_id.product_tmpl_id.code})
        return res

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.date_planned')
    def _compute_date_planned(self):
        for order in self:
            min_date = False
            for line in order.order_line:
                if not min_date or line.date_planned < min_date:
                    min_date = line.date_planned
            if min_date:
                order.date_planned = min_date
            else:
                order.date_planned = datetime.datetime.today()

    @api.model
    def get_date_planned(self):
        return datetime.datetime.today()

    date_planned = fields.Datetime(string='Scheduled Date', compute='_compute_date_planned', store=True, index=True, default=get_date_planned )