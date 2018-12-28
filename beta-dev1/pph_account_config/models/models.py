# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pph_account_config(models.Model):
    _name = 'pph.account.config'

    # name = fields.Char()
    # account_id = fields.Many2one('account.account', domain=[('deprecated', '=', False)], string='Tax Account',
    #                              ondelete='restrict',
    #                              help="Account that will be set on invoice tax lines for invoices. Leave empty to use the expense account.",
    #                              oldname='account_collected_id')
    # type_tax_use = fields.Selection([('sale', 'Sales'), ('purchase', 'Purchases'), ('none', 'None')],
    #                                 string='Tax Scope', required=True, default="sale",
    #                                 help="Determines where the tax is selectable. Note : 'None' means a tax can't be used by itself, however it can still be used in a group.")
    pph_account_purchase = fields.Many2one('account.account', string='PPH Account Purchase')
    pph_account_sales = fields.Many2one('account.account', string='PPH Account Sales')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = "%s" % ('PPH')
            result.append((record.id, name))
        return result
