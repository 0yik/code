from odoo import api, fields, models , _
import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import UserError,Warning

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_discount = amount_commission = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                if order.discount_type == 'percent':
                    amount_discount = (amount_untaxed * order.discount_rate) / 100
                    amount_tax = (((amount_untaxed - amount_discount) * order.tax_rate )/100)
            	if order.discount_type == 'amount':
            	    amount_discount = order.discount_rate
            	    amount_tax = order.tax_rate
                if order.commission_type == 'percent':
                    amount_commission = (((amount_untaxed -amount_discount + amount_tax) * order.commission_rate)/100)
            	if order.commission_type == 'amount':
            	    amount_commission = order.commission_rate

            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_discount': order.pricelist_id.currency_id.round(amount_discount),
                'amount_commission': order.pricelist_id.currency_id.round(amount_commission),
                'amount_total': (((amount_untaxed - amount_discount) - amount_commission)  + amount_tax)
            })
    
    
    tax_rate = fields.Float('Tax Rate', digits_compute=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    commission_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Commission Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    commission_rate = fields.Float('Commission Rate', digits_compute=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits_compute=dp.get_precision('Account'), track_visibility='always')
    amount_commission = fields.Monetary(string='Commission', store=True, readonly=True, compute='_amount_all',
                                      digits_compute=dp.get_precision('Account'), track_visibility='always')  
                                      
                                      
    @api.onchange('discount_type', 'discount_rate','tax_rate','commission_rate','commission_type')
    def supply_rate(self):
        amount_total = amount_discount = amount_tax = amount_commission = 0.0
        for order in self:
            if order.discount_type == 'percent':
                order.amount_discount = amount_discount = ((order.amount_untaxed * self.discount_rate)/100)
                order.amount_tax = amount_tax = (((order.amount_untaxed - order.amount_discount) * self.tax_rate) / 100)
                amount_total = (order.amount_untaxed + order.amount_tax ) - self.amount_discount
            if order.discount_type == 'amount':
                order.amount_discount = amount_discount = self.discount_rate
                order.amount_tax = amount_tax = self.tax_rate
                amount_total = (order.amount_untaxed + order.amount_tax ) - self.amount_discount
            if order.commission_type == 'percent':
                order.amount_commission = amount_commission = ((amount_total * self.commission_rate)/100)
            if order.commission_type == 'amount':
                order.amount_commission = amount_commission = self.commission_rate
            amount_total = (order.amount_untaxed + order.amount_tax ) - self.amount_discount
            order.amount_total = amount_total - order.amount_commission


                
    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate,
            'tax_rate': self.tax_rate,
            'commission_type': self.commission_type,
            'commission_rate': self.commission_rate
        })
        return invoice_vals

    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True
        
        
    @api.multi
    def action_confirm(self):
        discount_limit = self.env.ref('solum_sale_discount_total.discount_limit_verification').value
        warning_mess = {}
        for order in self:
            if order.amount_discount > 0:
                discount_rate = ((order.amount_discount*100)/ order.amount_untaxed)
                commission_rate = ((order.amount_commission*100) / (order.amount_untaxed - order.amount_discount))
                discount_commission_rate = discount_rate + commission_rate
                if float(discount_commission_rate) > float(discount_limit):
                     raise UserError(_('You will not apply discount more then %s%s !') % (discount_limit,'%'))
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
            message = ''
            for order_line in order.order_line:
                if order_line.product_id.is_pack:
                    if order_line.product_id.wk_product_pack:
                        for product_pack in order_line.product_id.wk_product_pack:
                            outgoing_qty = product_pack.product_name.outgoing_qty - order_line.product_uom_qty
                            available_qty = product_pack.product_name.qty_available - outgoing_qty
                            if available_qty < order_line.product_uom_qty:
                                lacking_qty = order_line.product_uom_qty - available_qty
                                message += _('You plan to sell %s of %s qty but you have only %s qty available! The lacking quantity is %s. \n')%\
                                    (str(product_pack.product_name.name), order_line.product_uom_qty, available_qty, lacking_qty)
                            
                else:    	
                    outgoing_qty = order_line.product_id.outgoing_qty - order_line.product_uom_qty
                    available_qty = order_line.product_id.qty_available - outgoing_qty
                    if available_qty < order_line.product_uom_qty:
                        lacking_qty = order_line.product_uom_qty - available_qty
                        message += _('You plan to sell %s of %s qty but you have only %s qty available! The lacking quantity is %s. \n')%\
                                    (str(order_line.product_id.name), order_line.product_uom_qty, available_qty, lacking_qty)
            if message:
                return self.get_warning_alert(message)
        return True


