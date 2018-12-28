# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_products_supplier_info(self):
        info_obj = self.env['product.supplierinfo']
        for record in self:
            if record and record.id:
                info_ids = info_obj.search([('name','=', record.id)])
                record.products_supplier_info = info_ids.ids or []

    customer_id = fields.Char('Customer ID')
    supplier_id = fields.Char('Supplier ID')
    products_supplier_info = fields.Many2many('product.supplierinfo', compute=_compute_products_supplier_info)
