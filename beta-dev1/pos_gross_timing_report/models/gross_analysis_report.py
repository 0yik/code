from odoo import fields, models, api, _, tools

class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    cost = fields.Float('Total Cost', readonly=True)
    total_gross = fields.Float('Total Gross', readonly=True)
    percentage_margin_against_price = fields.Float('% Margin against Price', group_operator="avg", readonly=True)
    percentage_cost_against_price = fields.Float('% Cost against Price', group_operator="avg", readonly=True)
    avg_cost = fields.Float('Average Cost', group_operator="avg", readonly=True)
    avg_margin = fields.Float('Average Margin', group_operator="avg", readonly=True)
    price_sub_total = fields.Float(string='Subtotal Price w/o discount', readonly=True)
    service_charge = fields.Float(string='Service Charge', readonly=True)
    pb1 = fields.Float(string='PB1', readonly=True)
    gross = fields.Float(string='Gross Price', readonly=True)
    avg_gross = fields.Float(string='Average Gross Price', readonly=True, group_operator="avg")

    product_category_id = fields.Many2one('pos.order.category', 'Product Order Category', readonly=True)
    avg_cooking_time_hour = fields.Float('Average Cooking Time(In Hours)', readonly=True)
    kitchen_config_id = fields.Many2one('pos.config', 'Kitchen Config', readonly=True)
    avg_customer_time_hour = fields.Float('Average Customer Time(In Hours)', readonly=True)
    avg_cooking_time_minute = fields.Float('Average Cooking Time(In Minutes)', readonly=True)
    avg_customer_time_minute = fields.Float('Average Customer Time(In Minutes)', readonly=True)
    forecast_time_seconds = fields.Float('Forecast Time (In Seconds)', readonly=True)
    forecast_time_minutes = fields.Float('Forecast Time (In Minutes)', readonly=True)
    # cancelled_product = fields.Many2one('product.product', string='Cancelled Product', readonly=True)
    cancel_manager = fields.Many2one('res.users', 'Cancel Approver', readonly=True)
    active = fields.Boolean('Active')
    mrp_bom_id = fields.Many2one('mrp.bom', string='Bill of Material')
    component_id = fields.Many2one('product.product','Component')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_pos_order')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW report_pos_order AS (
                        SELECT
                            SUM(l.cost) as cost,
                            SUM((l.qty * l.price_unit) - (l.cost)) AS total_gross,
                            CASE WHEN 
                                SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) = 0 then 0 
                            ELSE
                                (SUM((l.qty * l.price_unit) - (l.cost))) / SUM((l.qty * l.price_unit) * (100 - l.discount) / 100)
                            END AS percentage_margin_against_price,
                            CASE WHEN 
                                SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) = 0 then 0 
                            ELSE
                                (sum(l.cost) / SUM((l.qty * l.price_unit) * (100 - l.discount) / 100))
                            END AS percentage_cost_against_price,
                            sum(l.cost/l.qty) as avg_cost,
                            SUM(((l.qty * l.price_unit) - (l.cost))/l.qty) as avg_margin,
                            SUM(l.qty * l.price_unit) AS price_sub_total,
                            s.amount_service as service_charge,
                            s.amount_tax as pb1,
                            SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) + s.amount_tax + s.amount_service as gross,
                            (SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) + s.amount_tax + s.amount_service) / SUM(l.qty) as avg_gross,
                            pb.name AS brand,
                            pc.branch_id AS branch_id,
                            ROW_NUMBER() OVER () AS id,
                            -- MIN(o.id) AS id,
                            COUNT(*) AS nbr_lines,
                            s.date_order AS date,
                            MIN(l.qty) AS product_qty,
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
                            l.product_id,
                            CASE WHEN l.active = false
                                THEN l.cancel_manager
                                ELSE null END AS cancel_manager,
                            pt.categ_id AS product_categ_id,
                            o.current_screen AS kitchen_config_id,
                            p.product_tmpl_id,
                            ps.config_id,
                            pt.pos_categ_id,
                            pc.stock_location_id,
                            s.pricelist_id,
                            s.session_id,
                            s.invoice_id IS NOT NULL AS invoiced,
                            s.product_order_category_ids AS product_category_id,
                            s.city_id AS city_id,
                            bm.id AS mrp_bom_id,
                            bml.product_id AS component_id
                        FROM pos_order_line as l 
                            LEFT JOIN order_history o ON (l.uid=o.line_id)
                            LEFT JOIN pos_config ok ON (o.current_screen=ok.id)
                            LEFT JOIN pos_order s ON (s.id=l.order_id)
                            LEFT JOIN pos_order_category poc ON (s.product_order_category_ids=poc.id)
                            LEFT JOIN product_product p ON (l.product_id=p.id )
                            LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                            LEFT JOIN product_uom u ON (u.id=pt.uom_id)
                            LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                            LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
                            LEFT JOIN res_branch bi ON (pc.branch_id=bi.id)
                            LEFT JOIN product_brand pb ON (pb.id=bi.brand_id)
                            LEFT JOIN mrp_bom bm ON (bm.product_tmpl_id = pt.id)
                            LEFT JOIN mrp_bom_line bml ON (bml.bom_id = bm.id)
                        GROUP BY
                            s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                            s.user_id, s.location_id, s.company_id, s.sale_journal,
                            s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
                            l.product_id,
                            pt.categ_id, pt.pos_categ_id,
                            p.product_tmpl_id,
                            ps.config_id,
                            pc.stock_location_id,
                            s.product_order_category_ids,
                            pb.name,
                            pc.branch_id,o.current_screen,l.active,l.cancel_manager,bm.id,bml.product_id
                        HAVING
                            SUM(l.qty * u.factor) != 0
                        ORDER BY
                            id,order_id
                    )
                """)
