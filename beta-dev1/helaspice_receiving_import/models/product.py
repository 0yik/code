from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rack_location = fields.Char('Rack Location')
    repack_label = fields.Char('Repack Label')
    art_no = fields.Char('Art No')
    contents = fields.Char('Contents')
    directions_of_use = fields.Text('Directions of Use')
    ingredients = fields.Text('Ingredients')
    storage_place = fields.Text('Storage Place')

    @api.constrains('default_code')
    def unique_default_code(self):
        for record in self:
            if record.default_code:
                records = self.search([('id', '!=', record.id), ('default_code', 'like', record.default_code)])
                if records:
                    raise UserError('Product is already exist with same default code')

ProductTemplate()