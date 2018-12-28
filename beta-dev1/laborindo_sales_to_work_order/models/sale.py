from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    work_order_ids = fields.One2many('work.order.so','sale_order_id','Work Order')
    is_work_order = fields.Boolean('Is Work Order?')

    @api.multi
    def compute_work_order_count(self):
        for rec in self:
            rec.work_order_count = len(rec.work_order_ids)

    work_order_count = fields.Integer(compute='compute_work_order_count', string='Work Order Count')

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.work_order_ids:
            for wo in res.work_order_ids:
                wo.sale_order_id = res.id
        if res.order_line:
            if self.env['sale.order.line'].search([('product_id.category','=ilike','INSTRUMENT'),('order_id','=',res.id)]):
                res.is_work_order = True
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if self.work_order_ids:
            for wo in self.work_order_ids:
                wo.sale_order_id = self.id
        if self.order_line:
            sale_order_line_rec = self.env['sale.order.line'].search([('product_id.category','=ilike','INSTRUMENT'),('order_id','=',self.id)])
            if sale_order_line_rec:
                cr = self.env.cr
                cr.execute("""update sale_order set is_work_order='true' where id=%s;"""%(self.id))
        return res

    @api.multi
    def action_view_workorder(self):
        action = self.env.ref('laborindo_sales_to_work_order.action_work_order_labo').read()[0]
        action['domain'] = [('sale_order_id', 'in', self.ids)]
        return action

