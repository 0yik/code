# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class PosOrderReport(models.Model):
    _name = "report.pos.promotion"
    _description = "Point of Sale Promotion Statistics"
    _auto = False
    _order = 'date desc'

    date = fields.Datetime(string='Date Order', readonly=True)
    price_total = fields.Float(string='Total Price', readonly=True)
    price_sub_total = fields.Float(string='Subtotal w/o discount', readonly=True)
    total_discount = fields.Float(string='Total Discount', readonly=True)
    average_price = fields.Float(string='Average Price', readonly=True, group_operator="avg")
    nbr_lines = fields.Integer(string='# of Lines', readonly=True, oldname='nbr')
    product_qty = fields.Integer(string='Product Quantity', readonly=True)
    delay_validation = fields.Integer(string='Delay Validation')
    branch_id = fields.Many2one('res.branch', 'Branch')
    promotion_id = fields.Many2one('pos.promotion', 'Promotion')
    brand_id = fields.Many2one('product.brand', 'Brand')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_pos_promotion')
        self._cr.execute("""
            CREATE OR REPLACE VIEW report_pos_promotion AS (
                SELECT
                    MIN(l.id) AS id,
                    COUNT(*) AS nbr_lines,
                    s.date_order AS date,
                    SUM(l.qty) AS product_qty,
                    SUM(l.qty * l.price_unit) AS price_sub_total,
                    SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total,
                    SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount,
                    (SUM(l.qty*l.price_unit)/SUM(l.qty * u.factor))::decimal AS average_price,
                    SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                    s.id as order_id,
                    pc.branch_id AS branch_id,
                    pb.id AS brand_id,
                    pp.id AS promotion_id
                FROM pos_order_line AS l
                    LEFT JOIN pos_order s ON (s.id=l.order_id)
                    LEFT JOIN product_product p ON (l.product_id=p.id)
                    LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                    LEFT JOIN product_uom u ON (u.id=pt.uom_id)
                    LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                    LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
                    LEFT JOIN res_branch rb ON (pc.branch_id = rb.id)
                    LEFT JOIN product_brand pb ON (rb.brand_id = pb.id)
                    LEFT JOIN pos_config_promotion_rel ppr ON (pc.id = ppr.config_id)
                    LEFT JOIN pos_promotion pp ON (pp.id = ppr.promotion_id)
                WHERE l.promotion = True
                GROUP BY
                    s.id, 
                    s.date_order,
                    s.create_date,
                    l.product_id,
                    pp.id,
                    pb.id,
                    pc.branch_id
                HAVING
                    SUM(l.qty * u.factor) != 0
            )
        """)
