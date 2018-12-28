from odoo import fields,models,api,_

class consignment_invoice(models.Model):
    _name = 'consignment.invoice'

    name = fields.Char(string="Name")