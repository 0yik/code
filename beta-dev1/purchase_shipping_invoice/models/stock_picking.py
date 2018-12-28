from odoo import models, fields, api, _


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    shipement_invoice_created = fields.Boolean('Is Shipment Invoice Created', default=False)
