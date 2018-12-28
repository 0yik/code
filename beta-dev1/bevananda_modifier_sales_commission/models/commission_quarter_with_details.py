from odoo import api, fields, models, _, tools
from datetime import datetime


class commission_quarter_with_details(models.Model):
    _name = 'commission.quarter'
    
    name = fields.Char('Quarter Name', required=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
