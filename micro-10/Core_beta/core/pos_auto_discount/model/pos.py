from odoo import api, fields, models, _
from odoo.exceptions import UserError

class pos_discount(models.Model):

    _name = "pos.auto.discount"
    _rec_name = 'product_id'

    @api.multi
    def apply_discount_to_all_config(self):
        res = self.write({
            'state': 'active'
        })
        configs = self.env['pos.config'].search([('active', '=', True)])
        configs.write({
            'discount_ids': [(4, [self.id])]
        })
        return res

    @api.multi
    def stop_apply_discount_to_all_config(self):
        return self.write({
            'state': 'cancel'
        })

    @api.model
    def auto_stop_discount(self):
        discounts = self.search([('state', '=', 'active')])
        for disc in discounts:
            if fields.Datetime.now() >= disc.end_dt:
                disc.write({
                    'state': 'cancel'
                })
        return 1
    start_dt = fields.Datetime('Start date', required=1)
    end_dt = fields.Datetime('End date', required=1)
    product_id = fields.Many2one('product.product', string='Product Apply', domain=[('available_in_pos', '=', True)], required=1)
    category_id = fields.Many2one('pos.category', 'POS Category')
    state = fields.Selection([
        ('active', 'Active'),
        ('cancel', 'Cancel'),
    ], string='State', default='active')
    rule_ids = fields.One2many('pos.auto.discount.rule', 'discount_id', string='Rules')
    config_ids = fields.Many2many('pos.config', 'pos_discount_pos_config_rel', 'discount_id', 'config_id',
                                  string='Sessions Applied', readonly=1)

    _sql_constraints = [
        ('discount_product_unique', 'unique (product_id)', 'One product only one discount rule, please check your discount rule'),
    ]


class pos_discount_rule(models.Model):

    _name = 'pos.auto.discount.rule'

    discount_id = fields.Many2one('pos.auto.discount', 'Discount', required=1)
    list_price = fields.Float('Sale price', required=1)
    quantity = fields.Float('Quantity', required=1)
    state = fields.Selection(related='discount_id.state', string="State", store=1, readonly=1)

    @api.model
    def create(self, vals):
        if vals['list_price'] < 0 or vals['list_price'] > 100:
            raise UserError('Public price can not smaller 0 and greater 100')
        return super(pos_discount_rule, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.has_key('list_price') and vals.get('list_price'):
            if vals['list_price'] < 0 or vals['list_price'] > 100:
                raise UserError('Public price can not smaller 0 and greater 100')
        return super(pos_discount_rule, self).write(vals)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    discount_ids = fields.Many2many('pos.auto.discount', 'pos_discount_pos_config_rel' , 'config_id', 'discount_id', string='Discounts', domain=[('state', '=', 'active')])


