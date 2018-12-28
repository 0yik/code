from odoo import models, api, fields

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    drop_ship_address = fields.Boolean(string='Drop Ship Address')

    po_house_no = fields.Char(string="House No", )
    po_level_no = fields.Char(string="Level No", )
    po_unit_no = fields.Char(string="Unit No", )
    po_street = fields.Char()
    po_street2 = fields.Char()
    po_zip = fields.Char(change_default=True, )
    po_city = fields.Char()
    po_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', )
    po_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', )


purchase_order()
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    name = fields.Text('Description', required=False)

purchase_order_line()