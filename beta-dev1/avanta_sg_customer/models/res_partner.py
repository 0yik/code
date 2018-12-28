from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = "res.partner"

    source = fields.Text('Source')
    sources = fields.Many2one('product.product', 'Sources')

    property_payment_term_id = fields.Many2one('account.payment.term',
        string='Customer Payment Terms')
