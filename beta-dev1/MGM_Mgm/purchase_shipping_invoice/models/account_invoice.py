from odoo import models, fields, api, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_shipment_bill = fields.Boolean('Is Shipment Bill')
    po_reference = fields.Char(related='purchase_id.name', string = 'PO Reference')

