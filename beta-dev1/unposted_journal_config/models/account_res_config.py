from odoo import models, fields, api

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    group_customer_invoice_unpost = fields.Boolean('Customer Invoice', help="Allows you to create the journal entry with unposted state.")
    group_vendor_bill_unpost = fields.Boolean('Vendor Bill', help="Allows you to create the journal entry with unposted state.")

    @api.model
    def get_default_analytic_distribution_for_purchases(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        group_customer_invoice_unpost = False
        group_vendor_bill_unpost = False
        if fields:
            group_customer_invoice_unpost = IrConfigParam.sudo().get_param(
                'unposted_journal_config.customer_invoice_unpost')
            group_vendor_bill_unpost = IrConfigParam.sudo().get_param(
                'unposted_journal_config.vendor_bill_unpost')
        return {
            'group_customer_invoice_unpost': group_customer_invoice_unpost,
            'group_vendor_bill_unpost': group_vendor_bill_unpost
        }

    @api.multi
    def set_default_analytic_distribution_for_purchases(self):
        IrConfigParam = self.env['ir.config_parameter']
        for model in self:
            IrConfigParam.sudo().set_param('unposted_journal_config.customer_invoice_unpost',
                                           model.group_customer_invoice_unpost)
            IrConfigParam.sudo().set_param('unposted_journal_config.vendor_bill_unpost',
                                           model.group_vendor_bill_unpost)
