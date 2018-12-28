from odoo import api, fields, models, _
from pygments.lexer import _inherit


class pos_promotion_discount_order(models.Model):
    
    _inherit = "pos.promotion.discount.order"

    maximum_amount = fields.Float('Amount total (without tax) less or equal', required=1)