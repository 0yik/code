from odoo import fields, models, api

class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    shipment_invoice = fields.Selection([
        ('multiple', 'Allow Shipping Invoice with Multiple Shipment Document'),
        ('single', 'Shipment Invoice with One Shipment Document')
        ], "Shipping Invoice", default='single')

    @api.model
    def get_default_shipment_invoice(self, fields):
        shipment_invoice = False
        if 'shipment_invoice' in fields:
            shipment_invoice = self.env['ir.values'].get_default('purchase.config.settings', 'shipment_invoice', company_id=self.env.user.company_id.id)
        return {'shipment_invoice': shipment_invoice}

    @api.multi
    def set_default_shipment_invoice(self):
        for record in self:
            ir_values = self.env['ir.values'].sudo()
            ir_values.set_default('purchase.config.settings', 'shipment_invoice', record.shipment_invoice, company_id=self.env.user.company_id.id)