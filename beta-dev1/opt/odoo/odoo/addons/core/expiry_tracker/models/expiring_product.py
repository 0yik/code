
from odoo import tools
from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ExpiringProduct(models.Model):
    _name = "expiring.product"
    _auto = False
    _rec_name = 'created_date'
    _order = 'expiry_date desc'

    
    product_id = fields.Many2one('product.product',"Product")
    qty = fields.Float("Quantity")
    lot_id = fields.Many2one("stock.production.lot","Serial Number")
    created_date = fields.Datetime("Created Date")
    expiry_datetime = fields.Datetime("Expiry Date")
    expiry_date = fields.Date("Expiry Date")
    location_id = fields.Many2one('stock.location',string="Location")
    product_uom_id = fields.Many2one('product.uom', string='Unit of Measure', related='product_id.uom_id',readonly=True)
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query="""
        select min(q.id) as id,q.product_id as product_id, sum(q.qty) as qty, q.lot_id as lot_id, q.in_date as created_date,
            l.life_date as expiry_datetime,l.life_date::date as expiry_date, q.location_id as location_id
        from stock_quant q
        left join stock_location s on (s.id=q.location_id) 
        left join stock_production_lot l on (q.lot_id=l.id)
        where s.expiry_days != -1 and 
        l.life_date::date >= CURRENT_DATE and
        l.life_date::date <= CURRENT_DATE + s.expiry_days
        group by q.product_id, q.lot_id, q.in_date, l.life_date, q.location_id,expiry_date
        """
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)"""% (self._table,query))
        