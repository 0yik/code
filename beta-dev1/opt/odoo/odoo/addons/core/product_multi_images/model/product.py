# -*- coding: utf-8 -*-

from odoo import api, fields, models
from ast import literal_eval


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    description = fields.Char(string='Description')
    product_template_id = fields.Many2one('product.template',string='Product')

Attachment()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ir_attachment_ids = fields.One2many('ir.attachment','product_template_id',string='Image')

ProductTemplate()