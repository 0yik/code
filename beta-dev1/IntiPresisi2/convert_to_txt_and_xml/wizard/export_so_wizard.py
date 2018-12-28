# -*- coding: utf-8 -*-

from odoo import fields, models

class SoXmlFile(models.TransientModel):
    _name = 'so.xml.file'
    
    xml_file = fields.Binary(string='Xml File for Product')
    
    file_name = fields.Char(string='Xml File', size=64)
