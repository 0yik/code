from openerp import api, fields, models, _

class sale_order(models.Model):

    _inherit = "sale.order"

    promotion_ids = fields.Many2many('pos.promotion', 'pos_order_promotion_rel', 'order_id', 'promotion_id',
                                     string='Promotions program')

    @api.multi
    def apply_promotion_automatically(self):
        return True
    
    @api.multi
    def apply_promotion_manually(self):
        
        return True

class sale_order_line(models.Model):

    _inherit = "sale.order.line"

    promotion = fields.Boolean('Promotion', readonly=1)

