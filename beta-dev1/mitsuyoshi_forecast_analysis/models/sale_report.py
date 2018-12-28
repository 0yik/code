# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class SaleRequisitionLineInherited(models.Model):
    _inherit = "sale.requisition.line"

    qty_ordered = fields.Float(compute='_compute_ordered_qty', string='Ordered Quantities', store=True)

class forecast_analysis(models.Model):
    _name = "blanketorder.report"
    _description = "Blanket Orders Analysis"
    _rec_name = 'product_id'
    _auto = False
    # _auto = False
    # _order = 'date desc'

    date_end = fields.Datetime(string='Agreement deadline', readonly=True)
    ordering_date = fields.Datetime(string='Ordering date', readonly=True)
    delivery_date = fields.Datetime(string='Delivery Date', readonly=True)
    schedule_date = fields.Datetime(string='Schedule Date', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    user_id = fields.Many2one('res.users', string='Responsible', readonly=True)
    type_id = fields.Many2one('sale.requisition.type', string="Agreement Type")
    price_sub_total = fields.Float(string='Total Amount', readonly=True)
    product_qty = fields.Integer(string='Product Quantity', readonly=True)
    qty_ordered = fields.Integer(string='Ordered Qty', readonly=True)

    def _select(self):
        select_str = """
            SELECT min(l.id) as id, s.date_end AS date_end,
                    SUM(l.product_uom_qty) AS product_qty,
                    SUM(l.product_uom_qty * l.price_unit) AS price_sub_total,
                    s.partner_id AS partner_id,
                    s.ordering_date AS ordering_date,
                    s.schedule_date AS delivery_date,
                    s.type_id AS type_id,
                    s.user_id AS user_id,
                    l.product_id AS product_id,
                    l.schedule_date AS schedule_date,
                    l.qty_ordered AS qty_ordered
        """
        return select_str

    def _from(self):
        from_str = """
            sale_requisition_line AS l
                    LEFT JOIN sale_requisition s ON (s.id=l.requisition_id)
                    LEFT JOIN product_product p ON (l.product_id=p.id)
                    LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                    LEFT JOIN product_uom u ON (u.id=pt.uom_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """ GROUP BY
                    s.date_end, s.partner_id, 
                    s.user_id, s.ordering_date,s.schedule_date,s.type_id,
                    l.product_id,l.schedule_date,l.qty_ordered
                    """
        return group_by_str


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
