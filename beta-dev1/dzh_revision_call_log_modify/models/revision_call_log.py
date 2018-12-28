from odoo import api, fields, models

class revision_call_log(models.Model):
    _inherit = 'crm.phonecall'

    market_segment = fields.Many2one('market.segment',string="Market Segment")
    member_type = fields.Many2one('member.type',string="Member Type")
    product = fields.Many2many('product.product',string="Product")
    country = fields.Many2one('res.country',string="Country")
    source_id = fields.Many2one('utm.source',string="Source")
