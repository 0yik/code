from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    part_name = fields.Char("Part Name")
    pmb_no = fields.Char("PMB Number")
    customer_pmb_no = fields.Char("Part Number Customer")
    # mit_pmb_no = fields.Char("Part Number Mitsuyoshi")
    sup_no = fields.Char("Supplier Number")
    default_code = fields.Char('Part Number Mitsuyoshi')

    @api.multi
    def switch_data(self):
        template_ids = self.env['product.template'].search([])
        for record in template_ids:
            tmp = record.part_name
            record.part_name = record.customer_pmb_no or ''
            record.customer_pmb_no = tmp or ''






