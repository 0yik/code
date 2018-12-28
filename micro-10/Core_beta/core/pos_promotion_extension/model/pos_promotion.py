from odoo import api, fields, models, _


class pos_promotion(models.Model):
    _inherit= "pos.promotion"

    type = fields.Selection([
        ('1_discount_total_order', 'Discount on total order'),
        ('2_discount_category', 'Discount on categories'),
        ('3_discount_by_quantity_of_product', 'Discount by quantity of product'),
        ('4_pack_discount', 'By pack products discount products'),
        ('5_pack_free_gift', 'By pack products free products'),
        ('6_price_filter_quantity', 'Unit Price product filter by quantity'),
        ('7_total_price_filter_quantity', 'Total Price product filter by quantity'),
        ('8_payment_method_discount', 'Payment Method Discount')
    ], 'Type', required=1)
    payment_method_id = fields.Many2one('account.journal', string='Payment Method')
    bill_discount_vendor = fields.Boolean('Bill Discount to Partner')
    partner_id = fields.Many2one('res.partner', string='Partner')
    pos_promotion_discount_payment_ids = fields.One2many('pos.promotion.discount.payment', 'promotion_id', string='Discounts on Payment Method')

    @api.model
    def default_get(self, fields):
        res = super(pos_promotion, self).default_get(fields)
        products = self.env['product.product'].search([('name', '=', 'Promotion service')])
        if products:
            res.update({'product_id': products[0].id})
        return res


class pos_promotion_discount_order(models.Model):
    _name = "pos.promotion.discount.order"
    _order = "minimum_amount"

    minimum_amount = fields.Float('Amount total (without tax) greater or equal', required=1)
    discount = fields.Float('Discount %', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_discount_category(models.Model):
    _name = "pos.promotion.discount.category"
    _order = "category_id, discount"

    category_id = fields.Many2one('pos.category', 'POS Category', required=1)
    discount = fields.Float('Discount %', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_discount_quantity(models.Model):
    _name = "pos.promotion.discount.quantity"
    _order = "product_id"

    product_id = fields.Many2one('product.product', 'Product', domain=[('available_in_pos', '=', True)], required=1)
    quantity = fields.Float('Minimum quantity', required=1)
    discount = fields.Float('Discount %', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_gift_condition(models.Model):
    _name = "pos.promotion.gift.condition"
    _order = "product_id, minimum_quantity"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product',
                                 required=1)
    minimum_quantity = fields.Float('Qty greater or equal', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_gift_free(models.Model):
    _name = "pos.promotion.gift.free"
    _order = "product_id"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product gift',
                                 required=1)
    quantity_free = fields.Float('Quantity free', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_discount_condition(models.Model):
    _name = "pos.promotion.discount.condition"
    _order = "product_id, minimum_quantity"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product', required=1)
    minimum_quantity = fields.Float('Qty greater or equal', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_discount_apply(models.Model):
    _name = "pos.promotion.discount.apply"
    _order = "product_id"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product', required=1)
    discount = fields.Float('Discount %', required=1, default=1.0)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)


class pos_promotion_price(models.Model):
    _name = "pos.promotion.price"
    _order = "product_id, minimum_quantity"

    product_id = fields.Many2one('product.product', domain=[('available_in_pos', '=', True)], string='Product', required=1)
    minimum_quantity = fields.Float('Qty greater or equal', required=1)
    list_price = fields.Float('List Price', required=1)
    promotion_id = fields.Many2one('pos.promotion', 'Promotion', required=1)

class pos_promotion_discount_payment(models.Model):
    _name = 'pos.promotion.discount.payment'
    _description = 'Discounts on Payment Method'

    min_amount = fields.Float('Minimum Amount')
    max_amount = fields.Float('Maximum Amount')
    discount_type = fields.Selection([('fixed_amount','Fixed Amount'), ('percentage','Percentage')], string='Discount Type')
    discount_value = fields.Integer('Discount Value')
    promotion_id = fields.Many2one('pos.promotion', string='Promotion')

pos_promotion_discount_payment()