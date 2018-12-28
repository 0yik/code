from odoo import api, fields, models, _

class CatalogUom(models.TransientModel):
    _name = "wizard.catalog_select_uom"

    product_id = fields.Many2one('product.template', required=True)

    @api.multi
    def confirm_button(self):
        product_id = self.env['product.template'].browse(self.env.context.get('active_id', False))
        product_id.write({'uom_id': self.product_id.uom_id.id, 'uom_so_id': self.product_id.uom_so_id.id, 'uom_po_id': self.product_id.uom_po_id.id, })

class product_template(models.Model):
    _inherit = 'product.template'

    @api.multi
    def name_get(self):
        if self.env.context.get('is_choose_catelog', False):
            return [(template.id, '%s' % template.catelog_number) for template in self]
        return super(product_template,self).name_get()

