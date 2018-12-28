from odoo import models, fields, api, tools

# class product_template(models.Model):
#     _inherit = 'product.template'
#
#     standard_price = fields.Float(store=True)
#
# class product_product(models.Model):
#     _inherit = 'product.product'
#
#     standard_price = fields.Float(store=True)

class repair_report(models.Model):
    _name = 'mrp.repair.order'
    _auto = False

    product_id  = fields.Many2one('product.product', 'Product', readonly=True)
    product_line_id  = fields.Many2one('product.product', 'Component', readonly=True)
    user_id     = fields.Many2one('res.users','Salesperson')
    partner_id  = fields.Many2one('res.partner','Partner')
    state       = fields.Selection([('draft','Quotation'),('cancel','Cancelled'),
                                    ('confirmed','Confirmed'),('under_repair','Under Repair'),
                                    ('ready','Ready to Repair'),('2binvoiced','To be Invoiced'),
                                    ('invoice_expect','Invoice Exception'),('done','Repaired')],string='Status')
    subtotal    = fields.Float('Subtotal')
    # standard_price = fields.Float('Cost Involve')
    price_unit  = fields.Float('Unit Price')
    product_uom_qty = fields.Float('Component Quantity')
    # product_qty = fields.Float('Product Quantity')
    repair_id   = fields.Many2one('mrp.repair','Repair Order')
    type        = fields.Selection([('add','Add'),('remove','Remove')])
    # amount_total= fields.Float('Cost Involve')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'mrp_repair_order')
        self._cr.execute("""
                        CREATE or REPLACE view mrp_repair_order as (
                            SELECT 
                            min(mrl.id) as id,
                            mrl.product_id as product_line_id,
                            mrl.price_unit as price_unit,
                            mrl.product_uom_qty as product_uom_qty,
                            mrl.type as type,
                            mrl.repair_id as repair_id,
                            mr.product_id as product_id,
                            mr.user_id as user_id,
                            mr.state as state,
                            mr.partner_id as partner_id,
                            (mrl.price_unit * mrl.product_uom_qty) as subtotal
                            FROM mrp_repair_line mrl
                            INNER JOIN mrp_repair mr ON mr.id = mrl.repair_id 
                            GROUP BY mrl.id,mrl.repair_id,mr.product_id,mr.user_id,mr.state,mr.partner_id,mrl.product_id
                        )
                    """)
repair_report()

class repair_report_product(models.Model):
    _name = 'mrp.repair.order.product'
    _auto = False

    product_id  = fields.Many2one('product.product', 'Product', readonly=True)
    user_id     = fields.Many2one('res.users','Salesperson')
    partner_id  = fields.Many2one('res.partner','Partner')
    state       = fields.Selection([('draft','Quotation'),('cancel','Cancelled'),
                                    ('confirmed','Confirmed'),('under_repair','Under Repair'),
                                    ('ready','Ready to Repair'),('2binvoiced','To be Invoiced'),
                                    ('invoice_expect','Invoice Exception'),('done','Repaired')],string='Status')
    total_component = fields.Float('Total Component Quantity')
    product_qty = fields.Float('Product Quantity')
    repair_id   = fields.Many2one('mrp.repair','Repair Order')
    amount_total= fields.Float('Cost Involve')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'mrp_repair_order_product')
        self._cr.execute("""
                        CREATE or REPLACE view mrp_repair_order_product as (
                            SELECT 
                            min(mr.id) as id,
                            mr.id as repair_id,
                            mr.product_id as product_id,
                            mr.user_id as user_id,
                            mr.state as state,
                            mr.partner_id as partner_id,
                            mr.product_qty as product_qty,
                            mr.amount_total as amount_total,
                            sum(mrl.product_uom_qty) as total_component
                            FROM mrp_repair mr
                            INNER JOIN mrp_repair_line mrl ON mr.id = mrl.repair_id 
                            GROUP BY mr.id,mrl.repair_id,mr.product_id,mr.partner_id,mr.state,mr.user_id
                        )
                    """)
repair_report_product()