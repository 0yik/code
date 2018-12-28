from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    part_name = fields.Char("Part Name")
    pmb_no = fields.Char("PMB Number")
    customer_pmb_no = fields.Char("Part Number Customer")
    mit_pmb_no = fields.Char("Part Number Mitsuyoshi")
    sup_no = fields.Char("Supplier Number")
    mt = fields.Char(string="M/T")
    ct = fields.Float(string="CT")
    cav = fields.Float(string="Cav")







