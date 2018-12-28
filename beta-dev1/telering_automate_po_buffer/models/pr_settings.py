# -*- coding: utf-8 -*-

from odoo import api,_,fields,models
from odoo import tools
from datetime import date,timedelta

class Company(models.Model):
    _inherit = 'res.company'
    
    buffer_stock_per = fields.Float("Percentage Buffer Stock",default=0.0)
    
class PurchaseConfigSettingsInh(models.TransientModel):
    
    _inherit = 'purchase.config.settings'
    
    buffer_stock_per = fields.Float(related='company_id.buffer_stock_per',string="Percentage Buffer Stock")
    