from odoo import models,fields, api

class sale_order(models.Model):
    _inherit = 'sale.order'

    driver_id = fields.Many2one('driver', string='Driver')
    shipper_id = fields.Many2one('shipper', string='Shipper')