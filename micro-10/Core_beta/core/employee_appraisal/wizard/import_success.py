# -*- coding: utf-8 -*- 
from odoo import fields,models

class ImportSuccess(models.Model):
    _name = 'import.success'

    message = fields.Text('Message')
   
