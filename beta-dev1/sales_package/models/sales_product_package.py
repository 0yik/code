# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp


class product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def action_view_bookings(self):
        booking_line_ids = self.env['booking.order.line'].search([('product_id','=',self.id)])
        booking_ids = []
        for line in booking_line_ids:
            if line.order_id:
                booking_ids.append(line.order_id.id)
        
        view_id = self.env.ref('product_booking.view_tree_tree').id
        form_view_id = self.env.ref('product_booking.view_booking_order_view').id
        context = self._context.copy()
        return {
            'name':'form_name',
            'view_type':'form',
            'view_mode':'tree',
            'res_model':'booking.order',
            'view_id':view_id,
            'views':[(view_id,'tree'),(form_view_id,'form')],
            'type':'ir.actions.act_window',
            'domain':[('id','in',booking_ids)],
            'target':'current',
            'context':context,
        }
    
    @api.multi
    def get_booking_count(self):
        booking_line_ids = self.env['booking.order.line'].search([('product_id','=',self.id)])
        booking_ids = []
        for line in booking_line_ids:
            if line.order_id:
                booking_ids.append(line.order_id.id)
        self.bookings_count = len(booking_ids) or 0

    payment_terms = fields.One2many('package.payment.term', 'product_id')
    multi_product_image_ids = fields.One2many('multi.product.image', 'product_id')
    pack_line_ids = fields.One2many('product.pack.line', 'parent_product_id', 'Pack Products',
                                    help='List of products that are part of this pack.')
    bookings_count = fields.Float(compute='get_booking_count', string='Bookings Count')
    sell_price = fields.Float(string="Sale Price")


class multiple_product_image(models.Model):
    _name = 'multi.product.image'

    name = fields.Char(string="Name")
    product_id = fields.Many2one('product.product', string='Product')
    product_image = fields.Binary()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pack = fields.Boolean('Pack?', help='Is a Product Pack?')
    milestone_tmpl_id = fields.Many2one('milestone.template', string="Milestone Template")
    sale_terms_conditions_template_id = fields.Many2one('sale.tc', string="Terms and Conditions Template")
    pack_line_ids = fields.One2many('product.pack.line', 'parent_product_id', 'Pack Products',
                                    help='List of products that are part of this pack.')

class product_pack_line(models.Model):
    _name = 'product.pack.line'

    quantity = fields.Float('Quantity', default=1.0, digits=dp.get_precision('Product UoS'))
    product_id = fields.Many2one('product.product', 'Product', domain=[('pack', '=', False)])
    type = fields.Selection(related='product_id.product_tmpl_id.type')
    parent_product_id = fields.Many2one('product.product', 'Parent Product')
