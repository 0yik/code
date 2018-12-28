# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime,date, timedelta


class Partner(models.Model):
    _inherit = "res.partner"

    @api.one
    @api.constrains('customer_code')
    def _check_customer_code(self):
        customer_code = self.search([('customer_code', '!=', False),('customer_code', '=', self.customer_code)])
        if len(customer_code) > 1:
            raise ValidationError(_("Customer Code must be unique."))
	

    @api.model	
    def create(self, vals):
        if not vals.get('customer_code', False) and not vals.get('vendor_code', False):
            vals['customer_code'] = self.env['ir.sequence'].next_by_code('res.partner') or _('New')
        return super(Partner, self).create(vals)

    customer_code   = fields.Char('Code Customer')
    credit_limit    = fields.Integer('Credit Limit')
    tax_number      = fields.Char('Tax Number')
    is_member       = fields.Boolean('Member')
    city_code       = fields.Char('City Code')
    debit_limit     = fields.Float('Debit Limit')
    creation_date = fields.Date(default=date.today(), string='Create Date')
    create_by = fields.Many2one('res.users', string="Create By", default=lambda self: self.env.user)
