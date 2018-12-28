from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'

    customer_category = fields.Many2one('customer.category', string = 'Customer Category')
    vendor_category = fields.Many2one('vendor.category', string='Vendor Category')
    npwp_number = fields.Char('NPWP Number')
    npwp_address = fields.Char('NPWP Address')

Partner()

class CustomerCategory(models.Model):
    _name = 'customer.category'

    name = fields.Char(string = 'Customer Category')

CustomerCategory()


class VendorCategory(models.Model):
    _name = 'vendor.category'

    name = fields.Char(string='Vendor Category')


VendorCategory()
