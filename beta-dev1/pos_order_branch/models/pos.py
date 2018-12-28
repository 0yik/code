# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, tools, _
from functools import partial

class PosConfig(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch', 'Branch')
    charge = fields.Float(related="branch_id.servicecharge", store=True,help='this field is used to take service charge percentage from branch')

class pos_order(models.Model):
    _inherit = 'pos.order'

    branch_id = fields.Many2one('res.branch', 'Branch')
    
    @api.model
    def _order_fields(self, ui_order):
        res = super(pos_order, self)._order_fields(ui_order)
        res.update({'branch_id':   ui_order['branch_id']})
        return res
        
    @api.model
    def create_from_ui(self, orders):
        for order in orders:
            session_id = self.env['pos.session'].browse(order['data']['pos_session_id'])
            order['data'].update({'branch_id': session_id.config_id.branch_id.id})
        return super(pos_order, self).create_from_ui(orders)

class OrderCharge(models.Model):
    _name = 'order.charge'

    name = fields.Char(string='Name', required=True)
    type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], required=True)
    amount = fields.Float(string='Amount',)
    order_charge_account_id = fields.Many2one('account.account', 'Delivery Charge Account')
    order_charge_account_refund_id = fields.Many2one('account.account', 'Delivery Charge Account On Refunds')

class res_branch(models.Model):
    _name = 'res.branch'

    name = fields.Char('Name', required=True)
    address = fields.Text('Address', size=252)
    telephone_no = fields.Char("Telephone No")
    company_id =  fields.Many2one('res.company', 'Company', required=True)
    service_charge_id = fields.Many2one('service.charge', string = 'Service Charge')
    tax_id = fields.Many2one('account.tax', string='Tax')
    servicecharge = fields.Float('Service Charge')
    delivery_charge_id = fields.Many2one('order.charge', string="Delivery Charge")
    
class ServiceCharge(models.Model):
    _name = 'service.charge'

    name = fields.Char(string='Service Charge Name', required=True)
    service_charge_computation = fields.Selection([('fixed', 'Fixed'), ('percentage_of_price', 'Percentage Of Price')], required=True)
    amount = fields.Float(string='Amount',)
    service_charge_account_id = fields.Many2one('account.account', 'Service Charge Account')
    service_charge_account_refund_id = fields.Many2one('account.account', 'Service Charge Account On Refunds')

class PosOrderReport(models.Model):
    _inherit = "report.pos.order"
    
    branch_id = fields.Many2one('res.branch', 'Branch')

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
                    (SUM(l.qty*l.price_unit)/SUM(l.qty * u.factor))::decimal AS average_price,
                    SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                    s.id as order_id,
                    s.partner_id AS partner_id,
                    s.branch_id as branch_id,
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
                    s.invoice_id IS NOT NULL AS invoiced
                FROM pos_order_line AS l
                    LEFT JOIN pos_order s ON (s.id=l.order_id)
                    LEFT JOIN product_product p ON (l.product_id=p.id)
                    LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                    LEFT JOIN product_uom u ON (u.id=pt.uom_id)
                    LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                    LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
                GROUP BY
                    s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id, s.location_id, s.company_id, s.sale_journal,
                    s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
                    l.product_id,
                    pt.categ_id, pt.pos_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    pc.stock_location_id
                HAVING
                    SUM(l.qty * u.factor) != 0
            )
        """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
