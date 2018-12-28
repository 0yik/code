# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    service_charge_id = fields.Many2one('service.charge', string = 'Service Charge')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
