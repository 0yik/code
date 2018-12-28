from odoo import api, fields, models, tools

class product_analysis(models.Model):
    _name = 'purchase.report.analysis'
    _description = "Incoming Product Analysis"
    _auto = False
    # _order = 'date_order desc'

    #date_order = fields.Datetime('Order Date', readonly=True, help="Date on which this document has been created",
    #                             oldname='date')
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    unit_quantity = fields.Float('Product Quantity', readonly=True, oldname='quantity')
    receive_percentage = fields.Float(string="% Receive Product", readonly=True)
    buffer_percentage = fields.Float(string="% Buffer Product", readonly=True)
    qty_invoiced        = fields.Float(string='Billed Qty')
    qty_received        = fields.Float(string='Received Qty')
    qty_unreceived      = fields.Float(string='Unreceived Qty')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'purchase_report_analysis')
        self._cr.execute("""
                    CREATE or REPLACE view purchase_report_analysis as (
                        SELECT 
                        min(pp.id) as id,
                        tt.product_id as product_id,
                        tt.unit_quantity as unit_quantity,
                        tt.qty_unreceived as qty_unreceived,
                        tt.qty_received as qty_received,
                        tt.qty_invoiced as qty_invoiced,
                        tt.receive_percentage as receive_percentage,
                        tt.buffer_percentage as buffer_percentage
                        from (SELECT
                        DISTINCT pol.product_id as product_id,
                        sum(pol.product_qty) as unit_quantity,
                        sum(pol.qty_unreceived) as qty_unreceived,
                        sum(pol.qty_received) as qty_received,
                        sum(pol.qty_invoiced) as qty_invoiced,
                        ((sum(pol.qty_received)/sum(pol.product_qty))*100.0)::decimal(16,2) as receive_percentage,
                        ((sum(pol.product_qty - pol.qty_received)/sum(pol.product_qty))*100.0)::decimal(16,2) as buffer_percentage
                        from purchase_order_line pol 
                        GROUP BY pol.product_id) as tt
                        INNER JOIN product_product pp ON pp.id = tt.product_id 
                        GROUP BY tt.product_id,tt.unit_quantity,tt.qty_unreceived,tt.qty_received,tt.qty_invoiced,tt.receive_percentage,tt.buffer_percentage
                    )
                """ )

product_analysis()
