from odoo import models, fields, api

class product_template(models.Model):
    _inherit = 'product.template'

    terminal_ok = fields.Boolean('Terminal', default=False )
    terminal_amount = fields.Float(compute='_check_terminal')
    product_ids = fields.Many2many('product.template','dzh_modifier_fields_1707_product_rel','product_template_ids','product_ids')
    account_invoice_ids = fields.Many2many('account.invoice')

    @api.depends('terminal_ok')
    @api.onchange('terminal_ok')
    def _check_terminal(self):
        self.product_ids = self.env['product.template'].search([('terminal_ok', '=', True)])
        # for pro_list in self.product_ids:
            # self.account_invoice_ids = self.env['account.invoice'].search([('name','=',self.pro_list['name'])])
            # self.pro_list.terminal_amount = self.pro_list['']
        # product_obj = self.env['product.template']
        # for product in product_search:
        # if self.terminal_ok:
        #     if self.terminal_ok == False:
        #
        #         self.terminal_amount = 0
        #     else:
        #         self.terminal_amount = 1000
        # # return True