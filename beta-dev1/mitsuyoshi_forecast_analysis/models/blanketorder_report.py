# -*- coding: utf-8 -*-

from odoo import fields,_,models,api
from odoo import tools
import odoo.addons.decimal_precision as dp

class SaleRequisitionLineInherited(models.Model):
    _inherit = "sale.requisition.line"
    
    qty_ordered = fields.Float(compute='_compute_ordered_qty', string='Ordered Quantities',store=True)
    sub_total = fields.Float(compute="_compute_sub_total", string="Sub Total", 
                             digits=dp.get_precision('Product Price'),store=True)
    
class forecast_analysis(models.Model):
    
    _name = "blanketorder.report"
    _description = "Blanket Orders Analysis"
    _rec_name = 'product_id'
    _auto = False
    
    name = fields.Char('Order Reference', readonly=True)
    user_id = fields.Many2one("res.partner", string="Responsible",readonly=True)
    type_id = fields.Many2one('sale.requisition.type',"Agreement Type", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    date_end = fields.Datetime(string='Agreement Deadline', readonly=True)
    ordering_date = fields.Date(string="Ordering Date", readonly=True)
    delivery_date = fields.Date(string='Delivery Date', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_uom_qty = fields.Float('Qty', readonly=True)
    qty_ordered = fields.Float('Ordered Qty', readonly=True)
    schedule_date = fields.Date("Schedule Date", readonly=True)
    sub_total = fields.Float("Total", readonly=True)
    
    def _select(self):
        select_str = """
            SELECT min(l.id) as id,
            s.name as name,
            s.user_id as user_id,
            s.type_id as type_id,
            l.product_id as product_id,
            s.partner_id as partner_id,
            s.date_end as date_end,
            s.ordering_date as ordering_date,
            s.schedule_date as delivery_date,
            sum(l.product_uom_qty) as product_uom_qty,
            sum(l.qty_ordered) as qty_ordered,
            l.schedule_date as schedule_date,
            sum(l.sub_total) as sub_total
        """
        return select_str
    
    def _from(self):
        from_str = """
            sale_requisition_line l
                join sale_requisition s on (l.requisition_id=s.id)
                join res_partner partner on s.partner_id = partner.id
                join res_partner partner1 on s.user_id = partner1.id
                join sale_requisition_type type on s.type_id = type.id
                        left join product_product p on (l.product_id=p.id)
        """
        return from_str
            
    def _group_by(self):
        group_by_str = """ GROUP BY l.product_id,
                    l.requisition_id,
                    s.name,
                    s.type_id,
                    s.partner_id,
                    s.user_id,
                    s.date_end,
                    s.ordering_date,
                    s.schedule_date,
                    l.schedule_date
                    """
        return group_by_str
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
