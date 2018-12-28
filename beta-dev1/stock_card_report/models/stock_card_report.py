# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists


class StockCardReport(models.Model):
    _name = 'stock.card.report'
    _description = 'Stock Card Report'
    _auto = False

    branch_id = fields.Many2one("res.branch", string="Branch")
    product_id = fields.Many2one("product.product", string="Product")
    date = fields.Datetime()
    qty_in = fields.Float(string="In")
    total_cost = fields.Float(string="Cost")
    qty_out = fields.Float(string="Out")
    total_sale = fields.Float(string="Sales")
    qty_left = fields.Float(string="Qty left")
    gain_loss = fields.Float(string="Gain / Loss")

    def init(self):
        cr = self._cr
        drop_view_if_exists(cr, 'stock_card_report')
        cr.execute("""
            CREATE OR REPLACE VIEW stock_card_report AS (
                SELECT
                    sm.id AS id,
                    sm.branch_id AS branch_id,
                    sm.date AS date,
                    sm.product_id AS product_id,
                    CASE WHEN spt.code = 'outgoing'
                        THEN SUM(sm.product_uom_qty)
                    END AS qty_out,
                    CASE WHEN spt.code = 'incoming'
                        THEN SUM(sm.product_uom_qty)
                    END AS qty_in,
                    CASE WHEN spt.code = 'outgoing'
                        THEN SUM(sm.product_uom_qty * pt.list_price)
                    END AS total_sale,
                    CASE WHEN spt.code = 'incoming'
                        THEN SUM(sm.product_uom_qty * ir.value_float)
                    END AS total_cost,
                    CASE WHEN spt.code = 'outgoing'
                        THEN 0 - SUM(sm.product_uom_qty)
                        ELSE SUM(sm.product_uom_qty)
                    END AS qty_left,
                    CASE WHEN spt.code = 'outgoing'
                        THEN SUM(sm.product_uom_qty * pt.list_price)
                        ELSE 0 - SUM(sm.product_uom_qty * ir.value_float)
                    END AS gain_loss
                FROM
                    stock_move sm
                    JOIN stock_picking sp ON (sm.picking_id = sp.id)
                    JOIN stock_picking_type spt ON (sm.picking_type_id = spt.id)
                    JOIN product_product pp ON (sm.product_id = pp.id)
                    LEFT JOIN product_template pt ON (pp.product_tmpl_id = pt.id)
                    JOIN ir_property ir ON (split_part(res_id, ',', 2)::integer = pp.id)
                WHERE
                    sm.state = 'done' AND
                    spt.code IN ('outgoing', 'incoming') AND
                    ir.name = 'standard_price'
                GROUP BY
                    sm.id,
                    sm.branch_id,
                    sm.date,
                    sm.product_id,
                    spt.code,
                    sm.product_uom_qty,
                    pt.list_price,
                    ir.value_float
            )
        """)
