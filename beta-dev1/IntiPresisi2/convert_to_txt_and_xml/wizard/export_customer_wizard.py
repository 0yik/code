# -*- coding: utf-8 -*-

from odoo import fields, models

class CustomerTtxtFile(models.TransientModel):
    _name = 'customer.txt.file'
    
    txt_file = fields.Binary(string='Txt File for Product')
    
    file_name = fields.Char(string='Txt File', size=64)
