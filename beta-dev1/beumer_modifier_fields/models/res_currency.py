from odoo import api,models,fields

class res_currency(models.Model):
    _inherit = 'res.currency'

    country_id = fields.Many2one('res.country',string="Country")

    def get_country(self):
        currency_ids = self.search([])
        for currency_id in currency_ids:
            country_id = self.env['res.country'].search([('currency_id','=',currency_id.id)],limit=1)
            currency_id.country_id = country_id.id