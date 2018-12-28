from odoo import api, fields, models, _
from odoo.exceptions import UserError

class pos_product_variant(models.Model):

    _name = "pos.product.variant"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', 'Product', required=1)
    attribute_id1 = fields.Many2one('product.attribute', 'Attribute 1')
    value_id1 = fields.Many2one('product.attribute.value', string='Value 1')
    attribute_id2 = fields.Many2one('product.attribute', 'Attribute 2')
    value_id2 = fields.Many2one('product.attribute.value', string='Value 2')
    attribute_id3 = fields.Many2one('product.attribute', 'Attribute 3')
    value_id3 = fields.Many2one('product.attribute.value', string='Value 3')
    price_extra = fields.Float('Price extra', help='Price extra will include and base on product template', required=1)

class pos_product_combo(models.Model):
    _name = "pos.product.combo"
    _rec_name = "combo_id"

    product_id = fields.Many2one('product.product', 'Product', required=True, domain=[('available_in_pos', '=', True)])
    combo_id = fields.Many2one('product.product', 'Combo', required=True, domain=[('available_in_pos', '=', True)])
    quantity = fields.Float('Quantity', required=1, default=1)

    @api.model
    def create(self, vals):
        if vals['quantity'] < 0:
            raise UserError('Quantity can not smaller 0')
        return super(pos_product_combo, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals and vals.has_key('quantity') and vals.get('quantity') and vals.get('quantity') < 0:
            raise UserError('Quantity can not smaller 0')
        return super(pos_product_combo, self).write(vals)


class product_product(models.Model):
    _inherit = 'product.product'

    pos_product_combo_ids = fields.One2many('pos.product.combo', 'combo_id', string='Combos')
    pos_product_variant_ids = fields.One2many('pos.product.variant', 'product_id', 'Variants')
    pos_type = fields.Selection([
        ('none', 'None'),
        ('is_combo', 'Combo'),
        ('multi_variant', 'Variants')
    ], string='Pos type', default='none')

class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    size_id = fields.Many2one('product.attribute', 'Size/Attribute', readonly=1)
    variant_id = fields.Many2one('product.attribute.value', 'Variant/Value', readonly=1)




