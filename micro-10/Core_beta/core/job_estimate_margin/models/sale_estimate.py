# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

class SaleEstimateJob(models.Model):
    
    _inherit = "sale.estimate.job"

    expected_margin = fields.Float('Expected Margin')
    duration = fields.Integer('Duration')
    duration_type = fields.Selection([('days','Day(s)'), ('months','Month(s)'), ('years','Year(s)')])
    sale_order_ids  = fields.Many2many('sale.order',string='Quotations',compute='get_quotations')
    sale_count      = fields.Integer('Quotation Count',compute='get_quotations')



    @api.multi
    def _prepare_quotation_line(self,quotation):
        quo_line_obj = self.env['sale.order.line']
        for rec in self:
            for line in rec.estimate_ids:
                unit_price = (line.price_subtotal + (line.price_subtotal * rec.expected_margin) / 100) / line.product_uom_qty
                vals1 = {
                                'product_id':  line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit' : unit_price,
                                'price_subtotal': line.price_subtotal,
                                'name' : line.product_description,
                                'price_total' : self.total,
                                'discount' : line.discount,
                                'order_id':quotation.id,
                                }
                quo_line = quo_line_obj.create(vals1)
            for line in rec.labour_estimate_line_ids:
                unit_price = (line.price_subtotal + (line.price_subtotal * rec.expected_margin) / 100) / line.product_uom_qty
                vals1 = {
                                'product_id':  line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit' : unit_price,
                                'price_subtotal': line.price_subtotal,
                                'name' : line.product_description,
                                'price_total' : self.total,
                                'discount' : line.discount,
                                'order_id':quotation.id,
                                }
                quo_line = quo_line_obj.create(vals1)
                
            for line in rec.overhead_estimate_line_ids:
                unit_price = (line.price_subtotal + (line.price_subtotal * rec.expected_margin) / 100) / line.product_uom_qty
                vals1 = {
                                'product_id':  line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit' : unit_price,
                                'price_subtotal': line.price_subtotal,
                                'name' : line.product_description,
                                'price_total' : self.total,
                                'discount' : line.discount,
                                'order_id':quotation.id,
                                }
                quo_line = quo_line_obj.create(vals1)

    @api.multi
    def estimate_to_quotation(self):
        quo_obj = self.env['sale.order']
        quo_line_obj = self.env['sale.order.line']
        for rec in self:
            vals = {
                'partner_id': rec.partner_id.id,
                'origin': rec.number,
                'project_id': rec.analytic_id.id
            }
            quotation = quo_obj.create(vals)
            quotation.write({'sale_estimate_id': rec.id or False})
            rec._prepare_quotation_line(quotation)
            rec.quotation_id = quotation.id
            rec.state = 'quotesend'

    @api.multi
    def action_view_quotation(self):
        return {
            'name': _('Quotations'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'domain'    : [('id','in',self.sale_order_ids.ids)],
            'views': [(self.env.ref('sale.view_quotation_tree').id or False,'tree'),(self.env.ref('sale.view_order_form').id or False,'form')],
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.one
    def get_quotations(self):
        for record in self:
            record.sale_order_ids = self.env['sale.order'].search([('sale_estimate_id','=',record.id)])
            record.sale_count = len(record.sale_order_ids)


class sale_order(models.Model):
    _inherit = 'sale.order'

    sale_estimate_id  = fields.Many2one('sale.estimate.job')