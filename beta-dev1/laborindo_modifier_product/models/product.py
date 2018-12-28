from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class productTemplate(models.Model):
    _inherit = 'product.template'

    pack_stock_management = fields.Selection(
        [('decrmnt_pack', 'Decrement Pack Only'), ('decrmnt_products', 'Decrement Products Only'),
         ('decrmnt_both', 'Decrement Both')], 'Pack Stock Management', default='')
    type = fields.Selection([
        ('product', 'Stockable Product'), ('service', _('Service'))], string='Product Type', default='product', required=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')
    product_alias = fields.Char('Product Alias')
    brand = fields.Many2one('product.brand.list' ,string="Brand")
    category = fields.Many2one('product.category.list' ,string="Category")
    sub_category = fields.Many2one('product.sub.category.list' ,string="Sub-Category")
    catelog_number = fields.Char("Catalog Number")
    is_breakdown = fields.Boolean('Can be Breakdown')
    uom_so_id = fields.Many2one('product.uom', string="Sale Unit of Measure",required=True)

    @api.model
    def create(self,vals):
        print ">>>>vals>>>>",self._context
        res = super(productTemplate, self).create(vals)
        # print ">>>>>>res.uom_so_id>>>>",res.uom_so_id
        # if vals.get('uom_so_id'):
        #     res.uom_so_id = vals['uom_so_id']
        prod_obj = self.env['product.product'].search([('name','=',res.name)])
        if prod_obj:
            prod_obj.write({'uom_so_id': res.uom_so_id.id})
        return res

    @api.onchange('name')
    def product_alias_onchange(self):
        if self.name:
            self.product_alias = self.name
    minimum_purchase = fields.Float('Minimum Purchase',digits=dp.get_precision('Product Price'))
    minimum_sales = fields.Float('Minimum Sales', digits=dp.get_precision('Product Price'))


    @api.onchange('type')
    def onchange_type(self):
        if self.type != 'product':
            self.is_breakdown = False

    # @api.multi
    # @api.onchange('brand','category','sub_category')
    # def onchange_for_catelog_number(self):
    #     for rec in self:
    #         str_catelog_number = ''
    #         if rec.brand:
    #             str_catelog_number +=   rec.brand.line_code
    #         if rec.category:
    #             str_catelog_number += rec.category.line_code
    #         if rec.sub_category:
    #             str_catelog_number += rec.sub_category
    #         rec.catelog_number = str_catelog_number

    @api.onchange('pack_stock_management')
    def select_type_default_pack_mgmnt_onchange(self):
        if self.pack_stock_management:
            pk_dec = self.pack_stock_management
            if pk_dec == 'decrmnt_products':
                prd_type = 'service'
            elif pk_dec == 'decrmnt_both':
                prd_type = 'product'
            self.type = prd_type

    @api.onchange('catelog_number')
    def onchange_catelog_number(self):
        if self.catelog_number:
            self.default_code = self.catelog_number

    @api.onchange('uom_so_id')
    def onchange_uom_so(self):
        if self.uom_so_id:
            product_obj = self.env['product.product'].search([('name','=',self.name)])
            product_obj.write({'uom_so_id':self.uom_so_id.id})

class ProductProduct(models.Model):
    _inherit = "product.product"

    uom_so_id = fields.Many2one('product.uom',string="Sale Unit of Measure",required=True)

    @api.model
    def create(self,vals):
        # print "product . product>>>>>",vals['product_tmpl_id']
        if vals.get('uom_so_id',False):
            if vals.get('product_tmpl_id',False):
                obj = self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])])
                # print ">>>>>>>>>>",obj
                vals.update({
                    'uom_so_id' : obj.uom_so_id.id,
                })
            res = super(ProductProduct, self).create(vals)
            # print ">>>>>>>>>uom_so_id",res.uom_so_id
            res.uom_so_id = vals['uom_so_id']
            prod_obj = self.env['product.template'].search([('name','=',res.name)])
            if prod_obj:
                prod_obj.write({'uom_so_id':res.uom_so_id.id})
            return res
        else:
            return super(ProductProduct, self).create(vals)

    @api.onchange('uom_so_id')
    def onchange_uom_so(self):
        if self.uom_so_id and self.product_variant_id:
            prod_obj = self.env['product.template'].search([('id','=',self.product_variant_id.id)])
            prod_obj.write({'uom_so_id':self.uom_so_id.id})


    @api.onchange('pack_stock_management')
    def select_type_default_pack_mgmnt_onchange(self):
        if self.pack_stock_management:
            pk_dec = self.pack_stock_management
            if pk_dec == 'decrmnt_products':
                prd_type = 'service'
            elif pk_dec == 'decrmnt_both':
                prd_type = 'product'
            self.type = prd_type

    # @api.multi
    # @api.onchange('brand', 'category', 'sub_category')
    # def onchange_for_catelog_number(self):
    #     for rec in self:
    #         str_catelog_number = ''
    #         if rec.brand:
    #             str_catelog_number += rec.brand.line_code
    #         if rec.category:
    #             str_catelog_number += rec.category.line_code
    #         if rec.sub_category:
    #             str_catelog_number += rec.sub_category
    #         rec.catelog_number = str_catelog_number


