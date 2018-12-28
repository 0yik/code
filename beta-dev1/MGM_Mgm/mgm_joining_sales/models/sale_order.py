from odoo import models, fields, api, _ , exceptions
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import time
import itertools

class sale_order(models.Model):
    _inherit = 'sale.order'

    source_document = fields.Char('Source Document')

    @api.model
    def check_action(self, action):
        quotation_action    = self.env.ref('sale.action_quotations').id
        sale_action         = self.env.ref('sale.action_orders').id
        if action == quotation_action:
            return 'quotation'
        if action == sale_action:
            return 'sale'
        return True

class joining_sales_popup(models.TransientModel):
    _name = 'joining.sales'

    sale_ids    = fields.Many2many('sale.order',string='Quotation Name')
    so_date     = fields.Datetime('Quotation Date',default=fields.Date.today())
    product_ids  = fields.Many2many('product.product','product_joining_sale_rel', 'product_id', 'joining_id', string='Product Name',readonly=True)
    total_qty   = fields.Integer('Total Qty',readonly=True)
    description = fields.Text('Description Summary')
    default_code= fields.Char('Internal Reference',readonly=True)
    business_unit_id = fields.Many2one('business.unit', string='Business Unit', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(joining_sales_popup, self).default_get(fields)
        if self._context.get('active_ids',False) and self._context.get('active_model',False) == 'sale.order':
            sale_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
            if any(sale.state != 'draft' for sale in sale_ids):
                raise ValidationError(_("Joining Sale can be use for SO that have status Quotation!"))
            if len(sale_ids.mapped('partner_id')) != 1:
                raise ValidationError(_("The Quotation need be same customer!"))
            
            product = []
            business_unit = []
            common_business_unit = []
            product_list = []
            for order in sale_ids:
                product.append(order.order_line.mapped('product_id').ids)
                business_unit.append(order.business_unit_id.id)
                product_ids = order.order_line.mapped('product_id')
            for business_unit_a, business_unit_b in itertools.combinations(business_unit, 2):
                if business_unit_a != business_unit_b:
                    raise ValidationError(_("The Quotation need be same business unit!"))    
                common_business_unit.append(business_unit_a)
            #product_commons = list(set.intersection(*map(set, product)))
            
            qty = 0
            '''for so_record in sale_ids:
                for so_line in so_record.order_line:
                    for product_common in product_commons:
                        if so_line.product_id.id == product_common:
                            qty += so_line.product_uom_qty'''
                            
            for so_record in sale_ids:
                for so_line in so_record.order_line:
                    qty += so_line.product_uom_qty
                                
            #if not set.intersection(*map(set, product)):
            #    raise ValidationError(_("Please make sure have product in the selected Quotation"))
            #product = list(set.intersection(*map(set, product)))
            business_unit_id = self.env['product.product'].browse(common_business_unit[0])
            res['sale_ids'] = [(6, 0, self._context.get('active_ids', False))]
            res['business_unit_id'] = business_unit_id.id
            res['so_date'] = max(sale_ids.mapped('date_order'))
            for product_id in product:
                product_records = self.env['product.product'].browse(product_id)
                for product_record in product_records:
                    if product_record.id not in product_list:
                        product_list.append(product_record.id)
                    if product_record.default_code:
                        res['default_code'] = product_record.default_code
            res['product_ids']   = [(6, 0, product_list)]
            res['total_qty'] = qty
        return res

    @api.multi
    def joining_sales(self):
        order_id = self.sale_ids[0]
        name = ''
        count = 1
        for s in self.sale_ids:
            name += s.name
            if len(self.sale_ids) > count:
                name += ','
            count += 1
        sale_data = {
            'date_order'    : self.so_date,
            'warehouse_id'  : order_id.warehouse_id.id,
            'business_unit_id' : order_id.business_unit_id.id,
            'pricelist_id'  : order_id.pricelist_id.id,
            'picking_policy': order_id.picking_policy,
            'partner_shipping_id': order_id.partner_shipping_id.id,
            'partner_invoice_id'    : order_id.partner_invoice_id.id,
            'partner_id'    : order_id.partner_id.id,
            'currency_id'   : order_id.currency_id.id,
            'origin'        : name or '',
            'source_document' : name or '',
        }
        sale_data.update(self.env['sale.order'].default_get(['name']))
        sale = self.env['sale.order'].create(sale_data)
        for product_id in self.product_ids:
            lines = self.env['sale.order.line'].search([('order_id','in',self.sale_ids.ids),('product_id','=',product_id.id)])
            qty = 0
            for line in lines:
                qty += line.product_uom_qty
            line_data = {
                'product_id'    : product_id.id,
                'discount_rate' : 0,
                'product_uom'   : product_id.uom_id.id,
                'name'          : self.description or product_id.name,
                'product_uom_qty': qty,
                'price_unit'    : product_id.lst_price,
                'order_id'      : sale.id,
            }
            sale.write({'order_line':[(0,0,line_data)]})
        sale.write({'state':'sale'})
        for record in self.sale_ids:
            record.write({'state':'sale'})
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'res_id': sale.id or []
        }
