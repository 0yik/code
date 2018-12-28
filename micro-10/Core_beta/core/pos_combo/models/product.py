from odoo import api, fields, models, _
from odoo.exceptions import UserError

class pos_combo_item(models.Model):
    _name = "pos.combo.item"
    _rec_name = "product_combo_id"

    product_id = fields.Many2one('product.product', 'Product', required=True, domain=[('available_in_pos', '=', True)])
    product_combo_id = fields.Many2one('product.product', 'Combo', required=True, domain=[('available_in_pos', '=', True)])
    quantity = fields.Float('Quantity', required=1, default=1)
    default = fields.Boolean('Default', help='Default auto add to Order line')

    @api.model
    def create(self, vals):
        if vals['quantity'] < 0:
            raise UserError('Quantity can not smaller 0')
        return super(pos_combo_item, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals and vals.has_key('quantity') and vals.get('quantity') and vals.get('quantity') < 0:
            raise UserError('Quantity can not smaller 0')
        return super(pos_combo_item, self).write(vals)


class product_product(models.Model):
    _inherit = 'product.product'

    pos_combo_item_ids = fields.One2many('pos.combo.item', 'product_combo_id', string='Combo items')
    is_combo = fields.Boolean('Is combo')
    combo_limit = fields.Integer('Combo item limit', help='Limit combo items can allow cashier add / combo')





