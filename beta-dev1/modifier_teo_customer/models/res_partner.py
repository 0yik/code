# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'

    tax_id = fields.Many2one("account.tax", string="Tax")
    currency_id = fields.Many2one("res.currency", string="Currency")
    sales_term_id = fields.Many2one("account.payment.term", string="Sales Term")
    department_id = fields.Many2one("hr.department", string="Department")
    customer_name = fields.Char("Customer Name")
    supplier_name = fields.Char("Supplier Name")
