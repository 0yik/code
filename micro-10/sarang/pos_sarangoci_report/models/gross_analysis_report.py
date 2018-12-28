from odoo import fields, models, api, _, tools

class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    cost = fields.Float('Total Cost', readonly=True)
    mrp_bom_id = fields.Many2one('mrp.bom', string='Bill of Material', readonly=True)
    # mrp_bom_line_id = fields.Many2one('mrp.bom.line',string='Material line',readonly=True)
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

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(PosOrderReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                    orderby=orderby, lazy=lazy)
        return res

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_pos_order')
        self._cr.execute("""
            CREATE OR REPLACE VIEW report_pos_order AS (
                SELECT
                    MIN(l.id) AS id,
                    COUNT(*) AS nbr_lines,
                    s.date_order AS date,
                    SUM(l.qty) AS product_qty,
                    SUM(l.qty * l.price_unit) AS price_sub_total,
                    SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total,
                    SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount,
                    (SUM(l.qty*l.price_unit)/SUM(l.qty * u.factor))::decimal AS avg_price,
                    SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                    s.id as order_id,
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
                    
                    s.amount_service as service_charge,
                    s.amount_tax as pb1,
                    SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) + s.amount_tax + s.amount_service as gross,
                    (SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) + s.amount_tax + s.amount_service) / SUM(l.qty) as avg_gross,
                                        
                    s.partner_id AS partner_id,
                    s.state AS state,
                    s.user_id AS user_id,
                    s.location_id AS location_id,
                    s.company_id AS company_id,
                    s.sale_journal AS journal_id,
                    l.product_id AS product_id,
                    pt.categ_id AS product_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pt.pos_categ_id,
                    pc.stock_location_id,
                    s.pricelist_id,
                    s.session_id,
                    s.invoice_id IS NOT NULL AS invoiced,
                    pc.branch_id AS branch_id,
                    bm.id AS mrp_bom_id
                FROM pos_order_line AS l
                    LEFT JOIN pos_order s ON (s.id=l.order_id)
                    LEFT JOIN product_product p ON (l.product_id=p.id)
                    LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                    LEFT JOIN mrp_bom bm ON (bm.product_tmpl_id = pt.id)
                    LEFT JOIN product_uom u ON (u.id=pt.uom_id)
                    LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                    LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
                WHERE l.qty <> 0
                GROUP BY
                    s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id, s.location_id, s.company_id, s.sale_journal,
                    s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
                    l.product_id,
                    bm.id,
                    pt.categ_id, pt.pos_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pc.branch_id,
                    pc.stock_location_id
                HAVING
                    SUM(l.qty * u.factor) != 0
            )
        """)
