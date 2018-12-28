# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.depends('x_subscription_period', 'x_month_number')
    def compute_end_date(self):
        if not self.x_subscription_period:
            return
        month = self.x_month_number or 0
        start = datetime.strptime(self.x_subscription_period, '%Y-%m-%d')
        add_month = month % 12
        add_years = int(month/12) + (int(start.month) + add_month)/12
        end_month = (int(start.month) + add_month)%12 if (int(start.month) + add_month)/12 > 0  else int(start.month) + add_month
        end_year = start.year + add_years
        end_day = start.day
        while True:
            end_format = '%s-%s-%s' % (end_year, end_month, end_day)
            try:
                self.x_end_date = datetime.strptime(end_format, '%Y-%m-%d')
                break
            except:
                end_day -= 1


    x_subscription_period = fields.Date('Subscription Period', default=fields.Datetime.now)
    x_end_date = fields.Date("End Date", compute=compute_end_date)
    x_contact_term = fields.Text('Contract Term')
    x_month_number = fields.Integer('Number of Month', default=0)

    @api.onchange('partner_id')
    def onchange_partner_id_sale_order(self):
        if self.partner_id and self.partner_id.id:
            if self.order_line and len(self.order_line) > 0:
                self.order_line.write({'partner_from_so': self.partner_id.id})
        return



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_user_id = fields.Many2many("dzh.partner.user", id1='order_line_id', id2='sale_user_id', string="User ID")
    subscription_period = fields.Date('Subscription Period')
    start_date = fields.Datetime("Start Date", default=fields.Datetime.now)
    end_date = fields.Datetime("End Date", default=fields.Datetime.now)
    partner_from_so = fields.Many2one('res.partner', string='Partner ID')

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty=qty)
        if res:
            res.update({
                'account_user_id': self.sale_user_id.id,
                'subscription_period': self.subscription_period,
                'start_date': self.start_date,
                'end_date': self.end_date,
            })
        return res

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderLine, self).default_get(fields)
        if self._context.get('sale_order_partner_id', False):
            res['partner_from_so'] =  self._context.get('sale_order_partner_id', False)
        return res
