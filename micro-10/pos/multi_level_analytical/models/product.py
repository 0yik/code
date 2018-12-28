from odoo import fields, models,api

class ProductTemplate(models.Model):
    _inherit= 'product.template'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help='If user selected the product category, system will automatically fill in the Analytic Account.')

    @api.onchange('categ_id')
    def onchnge_product_category(self):
        if self.categ_id:
            self.analytic_account_id = self.categ_id.analytic_account_id