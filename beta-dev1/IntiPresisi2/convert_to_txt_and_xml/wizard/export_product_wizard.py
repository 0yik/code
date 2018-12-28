# -*- coding: utf-8 -*-

from odoo import fields, models
import base64

        
class ProducTtxtFile(models.TransientModel):
    _name = 'product.txt.file'
    
    txt_file = fields.Binary(string='Txt File for Product')
    
    file_name = fields.Char(string='Txt File', size=64)
