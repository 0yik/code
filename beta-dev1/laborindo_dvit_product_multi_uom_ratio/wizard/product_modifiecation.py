# coding=utf-8
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp

class WizTaskStockLines(models.TransientModel):
    _name = "wiz.prod.uom.line"


    wiz_id = fields.Many2one("wiz.prod.uom", string="prod_uom",)
    uom = fields.Char(string="Name")
    utype = fields.Selection(string='type', selection=[('smaller','Smaller'),('bigger','Bigger')], default='bigger')
    qty = fields.Float(string="Ratio", digits=dp.get_precision('Product Unit of Measure'), )
    usage = fields.Many2many('product.uom.type_multi_select', string='Usage')

    @api.constrains('usage')
    def usage_constrains(self):
        True

class WizProdUoM(models.TransientModel):
    _name = 'wiz.prod.uom'

    line_ids = fields.One2many("wiz.prod.uom.line", "wiz_id", string="UoMs")
    ref_uom = fields.Char(string="Main UoM", )
    product_id = fields.Many2one('product.template', string='Product', select=True,
        default=lambda self: self.env.context.get('active_id', False))

    @api.constrains('line_ids')
    def usage_constrains(self):
        list_usage = []
        for line in self.line_ids:
            if line.qty == 0:
                raise ValidationError(_('Ratio must be more than 0.'))
            for usage in line.usage:
                if usage.id in list_usage:
                    raise ValidationError(_('Usage must contains only one %s' %usage.name))
                list_usage.append(usage.id)
        if len(list_usage)< 2:
            raise ValidationError(_('Usage must have Sales and Purchase'))


    def create_uoms(self):
        product_id = self.product_id
        cat_name = (product_id.catelog_number if product_id.catelog_number else product_id.name).strip() + '_uoms'
        uom_categ_id = self.env['product.uom.categ'].create({'name': cat_name})
        ref_uom_id = self.env['product.uom'].create({
            'name': self.ref_uom,
            'uom_type': 'reference',
            'category_id': uom_categ_id.id,
            'rounding': 0.001,
            'factor': 1,
            'factor_inv': 1, })
        product_uom_po_id = False
        product_uom_so_id = False
        product_uom_id = False
        for line in self.line_ids:
            uom_id = self.env['product.uom'].create({
                'name' : line.uom,
                'uom_type' : line.utype,
                'factor_inv' : line.utype == 'bigger' and line.qty or (1 / abs(line.qty)),
                'factor' : line.utype == 'smaller' and abs(line.qty) or (1 / abs(line.qty)),
                'category_id' : uom_categ_id.id,
                'rounding' : 0.001,})
            if line.usage:
                list_type = list(map(lambda x: x.name ,line.usage))
                if 'Inventory' in list_type:
                    product_uom_id = uom_id.id
                if 'Sales' in list_type:
                    product_uom_so_id = uom_id.id
                if 'Purchase' in list_type:
                    product_uom_po_id = uom_id.id
        uom_vals = {'uom_id': ref_uom_id.id}
        if product_uom_so_id:
            uom_vals.update({
                'uom_so_id': product_uom_so_id
            })
        if product_uom_po_id:
            uom_vals.update({
                'uom_po_id': product_uom_po_id
            })
        product_id.write(uom_vals)
        return True

    @api.multi
    def add_uoms(self):
        uom_ids = self.create_uoms()

        return True

class uomusage(models.Model):
    _name = "product.uom.type_multi_select"

    name = fields.Char('Name',required=True)
