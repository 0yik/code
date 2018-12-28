# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class CustomSupplier(models.Model):
    _inherit = 'res.partner'

    supplier_id = fields.Char('Supplier ID', required=False)
