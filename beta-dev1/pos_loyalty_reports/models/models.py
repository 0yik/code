# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class pos_loyalty_reports(models.Model):
    _inherit = "report.pos.order"

    # loyalty_program

    customer = fields.Many2one('res.partner', string='Customer')
    loyalty_point = fields.Float('Loyalty Point')
    earning_points = fields.Float('Earning Points')
    loyalty_programs = fields.Many2one('loyalty.program', string='Loyalty Programs')
    rewards_items = fields.Many2one('loyalty.reward', string='Rewards Items')
    claimed_points = fields.Float('Claimed Points')
    net_points = fields.Float('Net Points')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_pos_order')
        self._cr.execute("""
            CREATE OR REPLACE VIEW report_pos_order AS (
                  SELECT
                    pb.name AS brand,
                    lr.point_cost AS claimed_points,
                    lp.id AS loyalty_programs,
                    s.reward_id AS rewards_items,
                    s.partner_id AS customer,
                    s.loyalty_points/ (select count(*) from pos_order_line where order_id = s.id) AS earning_points,
                    s.loyalty_points/ (select count(*) from pos_order_line where order_id = s.id) AS loyalty_point,
                    (COALESCE(s.loyalty_points,0) -  COALESCE(lr.point_cost,0)) AS net_points,
                    pc.branch_id AS branch_id,
                    -- MIN(o.id) AS id,
                    ROW_NUMBER() OVER () AS id,
                    COUNT(*) AS nbr_lines,
                    s.date_order AS date,
                    MIN(l.qty) AS product_qty,
                    MIN(l.qty * l.price_unit) AS price_sub_total,
                    MIN((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total,
                    MIN((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount,
                    (MIN(l.qty*l.price_unit)/MIN(l.qty * u.factor))::decimal AS average_price,
                    SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                    AVG((DATE_PART('day', (s.payment_date AT TIME ZONE 'UTC')
                                      - (s.date_order AT TIME ZONE 'UTC') ) * 3600 * 24
                    + DATE_PART('hour', (s.payment_date AT TIME ZONE 'UTC')
                                         - (s.date_order AT TIME ZONE 'UTC') ) * 3600
                    + DATE_PART('minute', (s.payment_date AT TIME ZONE 'UTC')
                                           - (s.date_order AT TIME ZONE 'UTC') ) *60
                    + DATE_PART('second', (s.payment_date AT TIME ZONE 'UTC')
                                           - (s.date_order AT TIME ZONE 'UTC') ))/3600) AS avg_customer_time_hour,
                    AVG(o.duration/3600.0) AS avg_cooking_time_hour,
                    AVG((DATE_PART('day', (s.payment_date AT TIME ZONE 'UTC')
                                      - (s.date_order AT TIME ZONE 'UTC') ) * 3600 * 24
                    + DATE_PART('hour', (s.payment_date AT TIME ZONE 'UTC')
                                         - (s.date_order AT TIME ZONE 'UTC') ) * 3600
                    + DATE_PART('minute', (s.payment_date AT TIME ZONE 'UTC')
                                           - (s.date_order AT TIME ZONE 'UTC') ) *60
                    + DATE_PART('second', (s.payment_date AT TIME ZONE 'UTC')
                                           - (s.date_order AT TIME ZONE 'UTC') ))/60) AS avg_customer_time_minute,
                    AVG(o.duration/60.0) AS avg_cooking_time_minute,
                    MIN(pt.normal_time_cook) AS forecast_time_seconds,
                    MIN(pt.normal_time_cook/60.0) AS forecast_time_minutes,
                    s.id as order_id,
                    s.partner_id AS partner_id,
                    s.state AS state,
                    s.user_id AS user_id,
                    s.location_id AS location_id,
                    s.company_id AS company_id,
                    s.sale_journal AS journal_id,
                    l.active as active,
                    CASE WHEN l.active = true
                        THEN l.product_id
                        ELSE null END AS product_id,
                    CASE WHEN l.active = false
                        THEN l.product_id
                        ELSE null END AS cancelled_product,
                    CASE WHEN l.active = false
                        THEN l.cancel_manager
                        ELSE null END AS cancel_manager,
                    pt.categ_id AS product_categ_id,
                    ok.id AS kitchen_config_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pt.pos_categ_id,
                    pc.stock_location_id,
                    s.pricelist_id,
                    s.session_id,
                    s.invoice_id IS NOT NULL AS invoiced,
                    s.city_id AS city_id,
                    s.product_order_category_ids AS product_category_id
                FROM pos_order_line as l 
                    LEFT JOIN order_history o ON (l.uid=o.line_id)
                    LEFT JOIN pos_config ok ON (o.current_screen=ok.id)
                    FULL JOIN pos_order s ON (s.id=l.order_id)
                    LEFT JOIN pos_order_category poc ON (s.product_order_category_ids=poc.id)
                    LEFT JOIN product_product p ON (l.product_id=p.id)
                    LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                    LEFT JOIN product_uom u ON (u.id=pt.uom_id)
                    LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                    LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
                    LEFT JOIN res_branch bi ON (pc.branch_id=bi.id)
                    LEFT JOIN product_brand pb ON (pb.id=bi.brand_id)
                    LEFT JOIN loyalty_reward lr ON (lr.id = s.reward_id)
                    LEFT JOIN loyalty_program lp ON (lp.id = lr.loyalty_program_id)
                GROUP BY
                    s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id, s.location_id, s.company_id, s.sale_journal,
                    s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
                    l.id,
                    l.product_id,
                    pt.categ_id, pt.pos_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pc.stock_location_id,
                    s.product_order_category_ids,
                    pb.name,
                    pc.branch_id,ok.id,
                    s.partner_id,
                    s.loyalty_points,
                    s.program_id,
                    s.reward_id,
                    lr.point_cost,
                    lp.id,
                    l.active,
                    l.cancel_manager
                HAVING
                    SUM(l.qty * u.factor) != 0
            )
        """)