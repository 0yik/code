from odoo import fields,models,api, tools, SUPERUSER_ID
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if self._context.get('search_default_opportunity_id',False):
            opportunity = self.env['crm.lead'].browse(self._context.get('search_default_opportunity_id',False))
            opportunity.planned_revenue = res.amount_total
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if vals.get('order_line',False) and self.opportunity_id:
            orders = self.search([('opportunity_id','=',self.opportunity_id.id)])
            if orders:
                max_order = max(orders.ids)
                order = self.browse(max_order)
                if order.id == self.id:
                    self.opportunity_id.planned_revenue = self.amount_total
        return res