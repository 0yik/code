# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class SaleReport(models.Model):
    _inherit = 'sale.report'

    part_number_id = fields.Many2one(
        comodel_name='sequence.number.product',
        string='Part Number', help='Part Number')
    prod_price = fields.Float('Price', readonly=True)
    partner_code = fields.Char('Customer Code')
    ordered_qty  = fields.Float('Qty')
    prod_price = fields.Float('Each')
    price_total = fields.Float('Amt')
    coating_en  = fields.Many2one('coating.enquiry','Coating')

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
             SELECT min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    l.part_number_product as part_number_id,
                    l.coating_en as coating_en,
                    l.price_unit as prod_price,
                    l.product_uom_qty as ordered_qty,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
                    sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
                    sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
                    sum(l.price_total / COALESCE(cr.rate, 1.0)) as price_total,
                    sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as price_subtotal,
                    count(*) as nbr,
                    s.name as name,
                    s.order_date as date,
                    s.state as state,
                    s.partner_id as partner_id,
                    partner.partner_code as partner_code,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.order_date)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    t.categ_id as categ_id,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    s.team_id as team_id,
                    p.product_tmpl_id,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight,
                    sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _from(self):
        from_str = """
                sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                    left join currency_rate cr on (cr.currency_id = pp.currency_id and
                        cr.company_id = s.company_id and
                        cr.date_start <= coalesce(s.order_date, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(s.order_date, now())))
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.order_id,
                    l.part_number_product,
                    l.price_unit,
                    t.uom_id,
                    t.categ_id,
                    s.name,
                    s.order_date,
                    s.partner_id,
                    s.user_id,
                    s.state,
                    s.company_id,
                    s.pricelist_id,
                    s.project_id,
                    s.team_id,
                    p.product_tmpl_id,
                    partner.country_id,
                    partner.commercial_partner_id,
                    partner.partner_code,
                    l.product_uom_qty,
                    l.coating_en
        """
        return group_by_str


