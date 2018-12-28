from odoo import models, fields, api

class sale_order(models.Model):
    _inherit = 'sale.order.line'

    part_name = fields.Char('Part Name')

    @api.onchange('product_id')
    def onchange_product_part_name(self):
        if self.product_id:
            self.part_name = self.product_id.part_name

    @api.onchange('part_name')
    def onchange_part_name_product(self):
        if self.part_name:
            template_ids = self.env['product.template'].search([('part_name','=',self.part_name)])
            if template_ids and len(template_ids) ==1 :
                self.product_id = template_ids.product_variant_id.id

class sale_requisition_line(models.Model):
    _inherit = 'sale.requisition.line'

    part_name = fields.Char('Part Name')
    part_number_mitsuyoshi = fields.Char('Part Number Mitsuyoshi')
    customer_pmb_no = fields.Char('Part Number Customer')

    @api.onchange('product_id')
    def onchange_product_part_name(self):
        if self.product_id:
            self.part_name = self.product_id.part_name
            self.part_number_mitsuyoshi = self.product_id.default_code
            self.customer_pmb_no = self.product_id.customer_pmb_no

    @api.onchange('part_name')
    def onchange_part_name_product(self):
        if self.part_name:
            template_ids = self.env['product.template'].search([('part_name', '=', self.part_name)])
            if template_ids and len(template_ids) == 1:
                self.product_id = template_ids.product_variant_id.id