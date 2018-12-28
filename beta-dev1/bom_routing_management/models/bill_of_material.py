# -*- coding: utf-8 -*-

from odoo import models, fields, api


class bom_routing_management(models.Model):
    _inherit = 'mrp.bom'

    @api.depends('recipe_ids')
    def _compute_mrp_bom_line(self):
        recipe_line_obj = self.env['mrp.bom.recipe.line']
        mrp_bom_line = self.env['mrp.bom.line']
        for record in self:
            try:
                if record.recipe_ids and len(record.recipe_ids) > 0:
                    record.bom_line_ids.unlink()
                    recipe_line_ids = recipe_line_obj.search([('recipe_id', 'in', record.recipe_ids.ids)])
                    product_ids = recipe_line_ids.mapped('product_id.id')
                    datas = {}
                    for product_id in product_ids:
                        material_qty = 0.0
                        match_recipe_line = recipe_line_ids.filtered(lambda x: x.product_id.id == product_id)
                        material_qty = sum(r.product_qty for r in match_recipe_line)
                        datas.update({str(product_id) : material_qty})
                    seq = 1
                    bom_line_ids = []
                    for data in datas.items():
                        new_line = mrp_bom_line.create({
                            'product_id' : int(data[0]),
                            'product_qty' : data[1],
                            'sequence' : seq,
                            'bom_id' : record.id,
                        })
                        bom_line_ids.append(new_line.id)
                        seq +=1
                    record.bom_line_ids = mrp_bom_line.browse(bom_line_ids)
            except:
                True
        return



    recipe_ids = fields.One2many('mrp.bom.recipe', 'bom_id', string="Recipe Line")
    bom_line_ids = fields.One2many('mrp.bom.line', 'bom_id', 'BoM Lines', copy=True, compute=_compute_mrp_bom_line)


class mrp_bom_recipe(models.Model):
    _name = 'mrp.bom.recipe'

    name = fields.Char('Step Name')
    step_seq = fields.Integer(string='Step Sequence')
    work_center = fields.Many2one('mrp.workcenter', string='Work Center')
    bom_id = fields.Many2one('mrp.bom', string='BOM ID')
    recipe_line = fields.One2many('mrp.bom.recipe.line', 'recipe_id', string='Recipe Line')


class mrp_bom_recipe_line(models.Model):
    _name = 'mrp.bom.recipe.line'

    name = fields.Char('Name')
    recipe_id = fields.Many2one('mrp.bom.recipe', string='Recipe ID')
    seq = fields.Integer('Sequence')
    product_id = fields.Many2one('product.product', string='Material')
    product_qty = fields.Float('Quantity')
    description = fields.Text('Description')
