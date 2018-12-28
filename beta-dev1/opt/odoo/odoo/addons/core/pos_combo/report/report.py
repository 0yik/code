# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists


class pos_combo_pack_report(models.Model):
    _name = "pos.combo.pack.report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Product Name', readonly=1)
    id = fields.Integer('Product Id', readonly=True)
    product_id = fields.Many2one('product.product', 'Template', readonly=1)
    qty = fields.Float('Quantity', readonly=1)
    sub_total = fields.Float('Sub total', readonly=1)
    date = fields.Datetime('Date Order', readonly=1)
    state = fields.Selection([
        ('draft', 'New'),
        ('cancel', 'Cancelled'),
        ('paid', 'Paid'),
        ('done', 'Posted'), (
            'invoiced', 'Invoiced')
    ], string='Status', readonly=1)
    pos_type = fields.Selection([
        ('none', 'None'),
        ('is customize', 'Is customize'),
        ('is_combo', 'Combo')
    ], string='Pos type', readonly=1)

    @api.model_cr
    def init(self): #v10
        drop_view_if_exists(self._cr, 'pos_combo_pack_report')
        self.env.cr.execute("""create or replace view pos_combo_pack_report as (
            SELECT p.id as id,
              p.id as product_id,
              pt.name as name,
              po.date_order as date,
              po.state as state,
              p.pos_type as pos_type,
              sum(pol.qty) as qty,
              sum(pol.qty * pol.price_unit * (1 - pol.discount / 100.0)) as sub_total
            FROM
              product_product p,
              product_template pt,
              pos_order po,
              pos_order_line pol
            WHERE
              p.product_tmpl_id = pt.id AND
              pol.product_id = p.id AND
              po.id = pol.order_id AND
              p.pos_type != 'none'
            GROUP BY p.id,
              po.date_order,
              po.state,
              p.pos_type,
              pt.id,
              pt.name
        )""")
