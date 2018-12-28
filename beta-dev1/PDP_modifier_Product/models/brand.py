# -*- coding: utf-8 -*-
from odoo import fields, models


class Brand(models.Model):
    _name = "brand.brand"
	
    name = fields.Char('Brand')
