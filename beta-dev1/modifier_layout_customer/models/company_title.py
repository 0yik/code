from odoo import api, fields, models, _

class CompanyTitle(models.Model):
    _name = 'company.title'

    name = fields.Char('Name')