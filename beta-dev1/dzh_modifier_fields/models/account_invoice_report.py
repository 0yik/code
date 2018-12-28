# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api

class AccountInvoiceReport_inherit(models.Model):
    _inherit = 'account.invoice.report'

    terminal_amount = fields.Float(string="Terminal Amount", readonly=True)
    total_amount = fields.Float("Monthly Revenue", readonly=True)
    data_amount = fields.Float(string="Data Amount", readonly=True)
    revenue_date = fields.Date("Revenue Date", readonly=True)
    x_subscription_period = fields.Date("Subscription Start Date", readonly=True)
    x_end_date = fields.Date("Subscription End Date", readonly=True)
    market_segment_id = fields.Many2one('market.segment','Market Segment')
    member_type_id = fields.Many2one('member.type','Member Type')



    _depends = {
        'account.invoice': [
            'account_id', 'amount_total_company_signed', 'commercial_partner_id', 'company_id',
            'currency_id', 'date_due', 'date_invoice', 'fiscal_position_id',
            'journal_id', 'partner_bank_id', 'partner_id', 'payment_term_id',
            'residual', 'state', 'type', 'user_id',
        ],
        'account.invoice.line': [
            'account_id', 'invoice_id', 'price_subtotal', 'product_id',
            'quantity', 'uom_id', 'account_analytic_id',
        ],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
        'product.uom': ['category_id', 'factor', 'name', 'uom_type'],
        'res.currency.rate': ['currency_id', 'name'],
        'res.partner': ['country_id','market_segment_id','member_type_id'],
        'monthly.revenue.line': ['account_invoice_id', 'terminal_amount', 'data_amount', 'total_amount', 'date','count_line_invoice'],
    }

    def _select(self):
        select_str = """
            SELECT sub.id, sub.date, sub.product_id, sub.partner_id, sub.country_id, sub.account_analytic_id,
                sub.payment_term_id, sub.uom_name, sub.currency_id, sub.journal_id,
                sub.fiscal_position_id, sub.user_id, sub.company_id, sub.nbr, sub.type, sub.state,
                sub.weight, sub.volume, 
                sub.categ_id, sub.date_due, sub.account_id, sub.account_line_id, sub.partner_bank_id,
                sub.product_qty, sub.price_total as price_total, sub.price_average as price_average,
                COALESCE(cr.rate, 1) as currency_rate, sub.residual as residual, sub.commercial_partner_id as commercial_partner_id,
                sub.terminal_amount, sub.total_amount, sub.data_amount, sub.revenue_date, sub.x_subscription_period,
                sub.market_segment_id, sub.member_type_id
        """
        return select_str

    def _sub_select(self):
        select_str = """
                SELECT ail.id AS id,
                    ai.date_invoice AS date,
                    ail.product_id, ai.partner_id, ai.payment_term_id, ail.account_analytic_id,
                    u2.name AS uom_name,
                    ai.currency_id, ai.journal_id, ai.fiscal_position_id, ai.user_id, ai.company_id, ai.x_subscription_period as x_subscription_period,
                    1 AS nbr,
                    ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
                    ai.partner_bank_id, mrl.count_line_invoice,
                    SUM (mrl.data_amount / mrl.count_line_invoice  ) AS data_amount,
                    SUM (mrl.terminal_amount / mrl.count_line_invoice ) AS terminal_amount,
                    SUM ((mrl.data_amount / mrl.count_line_invoice ) + (mrl.terminal_amount / mrl.count_line_invoice)) AS total_amount, mrl.date as revenue_date,
                    SUM ((invoice_type.sign * ail.quantity) / u.factor * u2.factor) AS product_qty,
                    SUM(ail.price_subtotal_signed) AS price_total,
                    SUM(ABS(ail.price_subtotal_signed)) / CASE
                            WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN SUM(ail.quantity / u.factor * u2.factor)
                               ELSE 1::numeric
                            END AS price_average,
                    ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
                    count(*) * invoice_type.sign AS residual,
                    ai.commercial_partner_id as commercial_partner_id,
                    partner.country_id,partner.market_segment_id as market_segment_id,partner.member_type_id as member_type_id,
                    SUM(pr.weight * (invoice_type.sign*ail.quantity) / u.factor * u2.factor) AS weight,
                    SUM(pr.volume * (invoice_type.sign*ail.quantity) / u.factor * u2.factor) AS volume
        """
        return select_str

    def _from(self):
        from_str = """
                FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON ai.commercial_partner_id = partner.id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                left JOIN product_template pt ON pt.id = pr.product_tmpl_id
                LEFT JOIN product_uom u ON u.id = ail.uom_id
                LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                LEFT JOIN monthly_revenue_line mrl ON mrl.account_invoice_id = ai.id
                JOIN (
                    -- Temporary table to decide if the qty should be added or retrieved (Invoice vs Refund) 
                    SELECT id,(CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN -1
                            ELSE 1
                        END) AS sign
                    FROM account_invoice ai
                ) AS invoice_type ON invoice_type.id = ai.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY ail.id, ail.product_id, ail.account_analytic_id, ai.date_invoice, ai.id,
                    ai.partner_id, ai.payment_term_id, u2.name, u2.id, ai.currency_id, ai.journal_id,
                    ai.fiscal_position_id, ai.user_id, ai.company_id, ai.type, invoice_type.sign, ai.state, pt.categ_id,
                    ai.date_due, ai.account_id, ail.account_id, ai.partner_bank_id, ai.residual_company_signed,
                    ai.amount_total_company_signed, ai.commercial_partner_id, partner.country_id,partner.market_segment_id,partner.member_type_id,
                    mrl.count_line_invoice, mrl.terminal_amount,mrl.data_amount, mrl.total_amount, mrl.date
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql = ("""CREATE or REPLACE VIEW %s as (
            WITH currency_rate AS (%s)
            %s
            FROM (
                %s %s %s
            ) AS sub
            LEFT JOIN currency_rate cr ON
                (cr.currency_id = sub.currency_id AND
                 cr.company_id = sub.company_id AND
                 cr.date_start <= COALESCE(sub.date, NOW()) AND
                 (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
        )""" % (
                    self._table, self.env['res.currency']._select_companies_rates(),
                    self._select(), self._sub_select(), self._from(), self._group_by()))
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            WITH currency_rate AS (%s)
            %s
            FROM (
                %s %s %s
            ) AS sub
            LEFT JOIN currency_rate cr ON
                (cr.currency_id = sub.currency_id AND
                 cr.company_id = sub.company_id AND
                 cr.date_start <= COALESCE(sub.date, NOW()) AND
                 (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
        )""" % (
                    self._table, self.env['res.currency']._select_companies_rates(),
                    self._select(), self._sub_select(), self._from(), self._group_by()))

class activity_report(models.Model):
    _inherit='crm.activity.report'

    x_subscription_period = fields.Date("Subscription Start Date", readonly=True)
    x_end_date = fields.Date("Subscription End Date", readonly=True)
    market_segment_id = fields.Many2one('market.segment', 'Market Segment')
    member_type_id = fields.Many2one('member.type', 'Member Type')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_activity_report')
        self._cr.execute("""
            CREATE VIEW crm_activity_report AS (
                select
                    m.id,
                    m.subtype_id,
                    m.author_id,
                    m.date,
                    m.subject,
                    l.id as lead_id,
                    l.x_subscription_period,
                    l.user_id,
                    l.team_id,
                    l.country_id,
                    l.company_id,
                    l.stage_id,
                    l.partner_id,
                    l.type as lead_type,
                    l.active,
                    l.probability,
                    partner.market_segment_id,
                    partner.member_type_id
                from
                    "mail_message" m
                join
                    "crm_lead" l
                on
                    (m.res_id = l.id)
                left join "res_partner" partner on (l.partner_id = partner.id)
                WHERE
                    (m.model = 'crm.lead')

            )""")

class mypipeline_report(models.Model):
    _inherit = 'crm.opportunity.report'

    x_subscription_period = fields.Date("Subscription Start Date", readonly=True)
    x_end_date = fields.Date("Subscription End Date", readonly=True)
    market_segment_id = fields.Many2one('market.segment', 'Market Segment')
    member_type_id = fields.Many2one('member.type', 'Member Type')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_opportunity_report')
        self._cr.execute("""
            CREATE VIEW crm_opportunity_report AS (
                SELECT
                    c.id,
                    c.date_deadline,

                    c.date_open as opening_date,
                    c.date_closed as date_closed,
                    c.date_last_stage_update as date_last_stage_update,
                    c.x_subscription_period,
                    c.user_id,
                    c.probability,
                    c.stage_id,
                    stage.name as stage_name,
                    c.type,
                    c.company_id,
                    c.priority,
                    c.team_id,
                    (SELECT COUNT(*)
                     FROM mail_message m
                     WHERE m.model = 'crm.lead' and m.res_id = c.id) as nbr_activities,
                    c.active,
                    c.campaign_id,
                    c.source_id,
                    c.medium_id,
                    c.partner_id,
                    c.city,
                    c.country_id,
                    c.planned_revenue as total_revenue,
                    c.planned_revenue*(c.probability/100) as expected_revenue,
                    c.create_date as create_date,
                    extract('epoch' from (c.date_closed-c.create_date))/(3600*24) as  delay_close,
                    abs(extract('epoch' from (c.date_deadline - c.date_closed))/(3600*24)) as  delay_expected,
                    extract('epoch' from (c.date_open-c.create_date))/(3600*24) as  delay_open,
                    c.lost_reason,
                    c.date_conversion as date_conversion,
                    partner.market_segment_id,
                    partner.member_type_id
                FROM
                    "crm_lead" c
                LEFT JOIN "crm_stage" stage
                ON stage.id = c.stage_id
                left join "res_partner" partner on partner.id = c.partner_id
                GROUP BY c.id, stage.name,partner.market_segment_id,partner.member_type_id
            )""")