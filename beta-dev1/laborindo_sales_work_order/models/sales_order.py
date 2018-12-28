# coding=utf-8
from odoo import api, fields, models

class WorkOrderLine(models.Model):
    _name = 'work.order.line'

    work_order_id = fields.Many2one('work.order', string='Work Order ID', copy=False)
    name = fields.Char('Work Order', related='work_order_id.name', readonly=True)
    contractor_id = fields.Many2one('res.partner', string='Sub Contractor')
    start_date = fields.Date('Scheduled Start Date', required=True)
    end_date = fields.Date('Scheduled End Date', required=True)
    percentage = fields.Integer('Percentage of Completion (%)')
    sale_order_line_id = fields.Many2one('sale.order.line', string='PO Line Reference')
    sale_order_id = fields.Many2one('sale.order', related='sale_order_line_id.order_id', string='PO Reference')
    state = fields.Selection([('draft', 'Waiting'), ('progress', 'In Progress'), ('done', 'Done')], related='work_order_id.state', string='Status')
    cost = fields.Float('Cost')

WorkOrderLine()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_category_instrument = fields.Boolean("Instrument Check", default=False, compute='compute_category')

    @api.multi
    # @api.depends('category')
    def compute_category(self):
        for rec in self:
            if rec.category.value is "INSTRUMENT":
                rec.is_category_instrument = True

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_category_instrument = fields.Boolean("Instrument Check", default=False, compute='compute_category')

    @api.multi
    # @api.depends('category')
    def compute_category(self):
        for rec in self:
            if rec.category.value is "INSTRUMENT":
                rec.is_category_instrument = True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def compute_work_order_count(self):
        for record in self:
            record.work_order_count = len(record.work_order_line_ids.ids)

    work_order_line_ids = fields.One2many('work.order.line', 'sale_order_line_id', 'Work Orders')
    product_type = fields.Selection(related="product_id.type", string='Product Type')
    is_category_instrument = fields.Boolean(related="product_id.is_category_instrument", string='Category')
    description = fields.Text('Description')
    work_order_count = fields.Integer(compute='compute_work_order_count', string='Work Order Count')

SaleOrderLine()


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def compute_work_order_count(self):
        for record in self:
            work_order_count = 0
            for line in record.order_line:
                work_order_count += len([1 for line2 in line.work_order_line_ids if line2.work_order_id])
            record.work_order_count = work_order_count


    work_order_count = fields.Integer(compute='compute_work_order_count', string='Work Order Count')

    @api.multi
    def button_confirm(self):
        super(SaleOrder, self).button_confirm()
        # Create work orders
        for record in self:
            for sales_line in record.order_line:
                for work_line in sales_line.work_order_line_ids:
                    vals = {}
                    vals['product_id'] = sales_line.product_id.id
                    vals['contractor_id'] = work_line.contractor_id.id
                    vals['partner_id'] = sales_line.partner_id.id
                    vals['start_date'] = work_line.start_date
                    vals['end_date'] = work_line.end_date
                    vals['percentage'] = work_line.percentage
                    vals['cost'] = work_line.cost
                    vals['sale_order_id'] = work_line.sale_order_id.id
                    vals['sale_order_line_id'] = work_line.sale_order_line_id.id
                    vals['currency_id'] = work_line.sale_order_id.currency_id.id
                    work_order_id = self.env['work.order'].create(vals)
                    work_line.work_order_id = work_order_id.id
        return True

    @api.multi
    def action_view_workorder(self):
        action = self.env.ref('laborindo_sales_work_order.action_work_order').read()[0]
        action['domain'] = [('sale_order_id', 'in', self.ids)]
        return action


SaleOrder()