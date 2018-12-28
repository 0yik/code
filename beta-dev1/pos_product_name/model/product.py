from odoo import api, fields, models, _
from odoo.exceptions import UserError

class product_product(models.Model):
    _inherit = 'product.product'


    image_exist1 = fields.Boolean('Image exist?', compute="_compute_image_exist", store=True)

    @api.multi
    @api.depends('image_medium')
    def _compute_image_exist(self):
        for rec in self:
            image_rec = self.env['ir.attachment'].search([('res_model', '=', 'product.template'),
                                                          ('res_field', '=', 'image'),
                                                          ('res_id', '=', rec.product_tmpl_id.id)])
            if image_rec:
                rec.image_exist1 = True
            else:
                rec.image_exist1 = False

