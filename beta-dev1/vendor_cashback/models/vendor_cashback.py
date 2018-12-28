# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class SaleOrder(models.Model):
    _inherit = "sale.order"
    is_sale_order = fields.Boolean(string='Is Sale Order', default=True)


class vendor_cashback(models.Model):
    _name = "vendor.cashback"
    _description = "Vendor Cashback"
    _auto = False
    _rec_name = 'partner_id'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(vendor_cashback, self.with_context(virtual_id=False)).read_group(domain, fields,
            groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for rt in res:
            if rt.has_key('is_sale_order'):
                if rt.get('is_sale_order', False):
                    rt['is_sale_order'] = 'Sales Order'
                else:
                    rt['is_sale_order'] = 'POS'
        return res

    def _get_data(self):
        for rec in self:
            total_amount = 0
            cash_back_per = 0
            order_ref = ''
            if rec.sale_order_id:
                order_ref = rec.sale_order_id.name
                total_amount = rec.sale_order_id.amount_total
                rec.date_order = rec.sale_order_id.date_order
            if rec.pos_order_id:
                order_ref = rec.pos_order_id.name
                total_amount = rec.pos_order_id.amount_total
                rec.date_order = rec.pos_order_id.date_order
            rec.total_amount = total_amount
            rec.cash_back_per = cash_back_per
            rec.order_ref = order_ref

    partner_id = fields.Many2one('res.partner', 'Customer')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    pos_order_id = fields.Many2one('pos.order', 'POS Order')
    order_ref = fields.Char(string='Order reference ', compute='_get_data')
    date_order = fields.Char(string='Order Date ', compute='_get_data')
    total_amount = fields.Float(string='Total', compute='_get_data')
    cash_back_per = fields.Float(string='Cash Back (%)', compute='_get_data')
    is_sale_order = fields.Boolean(string='Is Sale Order')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'vendor_cashback')
        self._cr.execute("""
        CREATE OR REPLACE VIEW vendor_cashback AS (
select ROW_NUMBER() OVER (ORDER BY rp.Name) as id, rp.id as partner_id,
mso.id as sale_order_id, mso.is_sale_order as is_sale_order, mpo.id as pos_order_id
from res_partner rp
full join (select so.id, so.is_sale_order as is_sale_order, so.partner_id, 'sale' as order_type from sale_order so where so.state in ('sale')) mso on rp.id=mso.partner_id
full join (select po.id, po.partner_id, 'pos' as order_type from pos_order po where po.state not in ('draft','cancel')) mpo on rp.id=mpo.partner_id
where mso.id is not null or mpo.id is not null
        )""")
