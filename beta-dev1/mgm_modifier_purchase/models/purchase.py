from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.price_total','discount_type','discount_rate')
    @api.onchange('discount_type','discount_rate')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                if line.discount_type == 'percent':
                    amount_tax += ((line.price_subtotal - ((line.price_subtotal * 10)/100))*10)/100
                    amount_discount += ((line.product_qty * line.price_unit) * (line.discount_rate / 100))
                else:
                    amount_tax += ((line.price_subtotal * 10)/100)
                    amount_discount += line.discount_rate
                #amount_tax += line.price_tax
                
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_discount': order.pricelist_id.currency_id.round(amount_discount),
                'amount_total': amount_untaxed + amount_tax,
            })
            
    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_rate','additional_amount')
    def _calculate_amount_all(self):
        """
        Compute the total amounts of the po.
        """
        unit_price = 0
        total_netto = 0
        discount_rate_value = 0

        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0

            for line in order.order_line:
                unit_price = unit_price + (line.price_unit * line.product_qty)
                total_netto = total_netto + (line.price_unit * line.product_qty) - line.price_subtotal
                amount_untaxed += (line.product_qty * line.price_unit)

                if line.discount_type == 'percent':
                    amount_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                    if order.discount_type == 'percent':
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
                            discount_rate_value = order.amount_discount

                    else:
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                            #order.amount_discount = (calculate_discount + order.discount_rate)
                            order.amount_discount = order.discount_rate
                            discount_rate_value = order.amount_discount

                else:
                    #amount_discount += (line.discount_rate * line.product_qty)
                    amount_discount += line.discount_rate
                    if order.discount_type == 'percent':
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                            order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
                            discount_rate_value = order.amount_discount

                    else:
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_qty * line.price_unit * line.discount_rate) / 100
                            #order.amount_discount = (calculate_discount + order.discount_rate)
                            order.amount_discount = order.discount_rate
                            discount_rate_value = order.amount_discount

                amount_tax += line.price_tax

            untaxed_amount = order.currency_id.round(amount_untaxed)
            if order.discount_type and order.discount_rate:
                order.update({
                    'cal_add_price': order.additional_amount,
                    'amount_untaxed': untaxed_amount,
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_discount': order.currency_id.round(discount_rate_value),
                    'amount_total': untaxed_amount - discount_rate_value + amount_tax + order.additional_amount,
                })
            else:
                order.update({
                    'cal_add_price': order.additional_amount,
                    'amount_untaxed': untaxed_amount,
                    'amount_tax': order.currency_id.round(amount_tax),
                    'amount_discount': order.currency_id.round(amount_discount),
                    'amount_total': untaxed_amount - amount_discount + amount_tax + order.additional_amount,
                })
                        
    reference_number = fields.Char('Reference Number', size=30)
    asset_id = fields.Many2one('account.asset.asset', 'Asset')

# class PurchaseProductCode(models.Model):
#     _name = 'purchase.product.code'
#
#
#     name = fields.Char('Product Code')
#
#     def cron_get_product_code(self):
#         product_ids = self.env['product.product'].search([])
#         for product in product_ids.filtered(lambda r: r.default_code):
#             product_code_id = self.search([('name', '=', product.default_code)], limit=1)
#             if not product_code_id:
#                 product_code_id = self.create({'name': product.default_code})
#         return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    def get_product_code(self):
        lst = []
        product_ids = self.env['product.product'].search([])
        for product in product_ids.filtered(lambda r: r.default_code):
            lst.append((product.id, product.default_code))
        return lst

    # def cron_get_product_code(self):
    #     product_ids = self.env['product.product'].search([])
    #     for product in product_ids.filtered(lambda r: r.default_code):
    #         product_code_id = self.env['purchase.product.code'].search([('name', '=', product.default_code)], limit=1)
    #         if not product_code_id:
    #             product_code_id = self.env['purchase.product.code'].create({'name': product.default_code})
    #     return True

    # product_code = fields.Selection(get_product_code, string='Product Code')
    # product_code_id = fields.Many2one('purchase.product.code', string='Product Code')
    #
    # @api.onchange('product_code_id')
    # def onchange_product_code_id(self):
    #     if self.product_code_id:
    #         product_id = self.env['product.product'].search([('default_code', '=', self.product_code_id.name)], limit=1)
    #         if product_id:
    #             self.product_id = product_id.id

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            if line.discount_type and line.discount_rate:
                if line.discount_type == 'percent':
                    price_unit = line.price_unit * (1 - (line.discount_rate or 0.0) / 100.0)
                    taxes = line.taxes_id.compute_all(price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
                    line.update({
                        #'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_tax': (taxes['total_excluded'] * 10 )/100,
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })  
                    line.total = line.price_subtotal + ((line.price_subtotal * 10)/100)
                elif line.discount_type == 'amount':
                    price_unit = line.price_unit   
                    taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
                    #taxes['total_excluded'] =taxes['total_excluded'] 
                    line.update({
                        #'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_tax': (((taxes['total_excluded'] - line.discount_rate)* 10 )/100),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'] - line.discount_rate,
                    }) 
                    line.total = line.price_subtotal + ((line.price_subtotal * 10)/100)
            else:
                taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
                line.update({
                    #'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_tax': (taxes['total_excluded'] * 10 )/100,
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
                line.total = line.price_subtotal + ((line.price_subtotal * 10)/100)
    
    product_code = fields.Many2one('product.code', string="Product Code")
    total = fields.Monetary(compute='_compute_amount', string='Total', store=True)

    @api.onchange('product_code')
    def onchange_product_code(self):
        self.product_id = False
        if self.product_code.name:
            product = self.env['product.product'].search([('default_code','=',self.product_code.name)])
            if product:
                self.product_id = product.id
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        if self.product_id:
            if self.product_id.default_code:
                product_code = self.env['product.code'].search([('name','=',self.product_id.default_code)], limit=1)
                self.product_code = product_code.id
            else:
                self.product_code = False
        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            #self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        #else:
            #self.taxes_id = fpos.map_tax(self.product_id.supplier_compute_alltaxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result
            
        
    @api.onchange('discount_type', 'discount_rate')
    def discount_onchange(self):
        for rec in self:
            if not rec.discount_type:
                rec.discount_rate = 0.0
            if rec.discount_type and rec.discount_rate:
                subtotal = rec.price_unit * rec.product_qty
                price = 0
                if rec.discount_type == 'percent':
                    price = rec.price_unit * (1 - (rec.discount_rate or 0.0) / 100.0)
                    rec.discount = ((rec.price_unit * rec.product_qty) * rec.discount_rate) / 100
                    taxes = rec.taxes_id.compute_all(price, rec.order_id.currency_id, rec.product_qty,
                                                  product=rec.product_id, partner=rec.order_id.partner_id)
                    rec.update({
                        'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
                    
                elif rec.discount_type == 'amount':
                    #rec.discount = ((rec.price_unit * rec.product_qty) - rec.discount_rate)
                    price = rec.price_unit
                    rec.discount = rec.discount_rate

                    taxes = rec.taxes_id.compute_all(price, rec.order_id.currency_id, rec.product_qty,
                                                      product=rec.product_id, partner=rec.order_id.partner_id)
                    taxes['total_excluded'] =taxes['total_excluded'] - rec.discount_rate
                    rec.update({
                        'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    origin = fields.Many2one('purchase.request', string="Source Document")
    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    date_end = fields.Date(string="Due Date")

    @api.onchange('ordering_date')
    def onchange_ordering_date_to(self):
        if self.ordering_date:
            self.date_end = self.ordering_date

    @api.onchange('origin')
    def onchange_origin(self):
        self.date_end = False
        self.ordering_date = False
        self.schedule_date = False

        if self.origin:
            self.date_end = self.origin.due_date
            self.ordering_date = self.origin.request_date

class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'
    
    product_code = fields.Many2one('product.code', string="Product Code")
    
    @api.onchange('product_code')
    def onchange_product_code(self):
        self.product_id = False
        if self.product_code.name:
            product = self.env['product.product'].search([('default_code','=',self.product_code.name)])
            if product:
                self.product_id = product.id
                
    @api.onchange('product_id', 'product_uom_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            #self.product_code = False
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
                product_code = self.env['product.code'].search([('name','=',self.product_id.code)], limit=1)
                self.product_code = product_code.id
            else:
                #print"\n product code is not avaialable"
                self.product_code = False
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name                
                
class ProductCode(models.Model):
    _name = 'product.code' 
    
    name = fields.Char("Product Code")  
    
    @api.model_cr
    def init(self):
        product_ids = self.env['product.product'].search([])
        for product in product_ids.filtered(lambda r: r.default_code):
            if not self.env["product.code"].search([('name','=',product.default_code)]):
                self.env["product.code"].create({'name':product.default_code,})
        return super(ProductCode,self).init()

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'     
    
    @api.model
    def _get_default_requested_by(self):
        return self.env.user.id
        
    requested_by = fields.Many2one('res.users', 'Requested by', required=True, track_visibility='onchange', default=_get_default_requested_by)
    
    @api.onchange('requested_by')
    def onchange_requested_by(self):
        if self.requested_by:
            employee = self.env["hr.employee"].search([('user_id','=',self.requested_by.id)], limit=1)
            self.department_id = employee.department_id

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    delivery_document = fields.Many2one('stock.picking',compute="_compute_delivery_doc")

    @api.depends('purchase_id','origin')
    @api.multi
    def _compute_delivery_doc(self):
        for rec in self:
            purchase = rec.purchase_id.search([('name','=',rec.origin)], limit=1)
            if purchase and purchase.picking_ids:
                if len(purchase.picking_ids) > 1:
                    rec.delivery_document = purchase.picking_ids[0]
                else:
                    rec.delivery_document = purchase.picking_ids