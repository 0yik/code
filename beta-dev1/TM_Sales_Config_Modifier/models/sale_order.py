from odoo import models, fields, api



class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    printout_sale_order = fields.Selection([
        ('used', "Use Product Promotion Service at printout"),
        ('unused', "Do not use (show) Promotion Service at printout")
    ], string='Printout config', default='used')

    @api.multi
    def set_printout_sale_order(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'printout_sale_order', self.printout_sale_order)