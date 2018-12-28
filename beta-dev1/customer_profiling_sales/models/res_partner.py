# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _
import operator as py_operator

OPERATORS = {
        '<': py_operator.lt,
        '>': py_operator.gt,
        '<=': py_operator.le,
        '>=': py_operator.ge,
        '=': py_operator.eq,
        '!=': py_operator.ne
}


class ResPartber(models.Model):
    _inherit = 'res.partner'

    @api.one
    @api.depends('sale_order_count')
    def _get_total_sale(self):
        for self_obj in self:
            sale_total_amount = 0.0
            for sale_obj in self.sale_order_ids:
                sale_total_amount += sale_obj.amount_total
            self_obj.sale_count = sale_total_amount

    def _search_sale_amount(self, operator, value):
        #search_ids = self.search([])
        ids = []
        for search in self.search([]):
            if OPERATORS[operator](search.sale_count, value):
                ids.append(search.id)
        return [('id', 'in', ids)]


    sale_count = fields.Float(
        string='Sales Amount',  compute='_get_total_sale',
        search='_search_sale_amount',
        help='Sales Amount')
    product_cat_id = fields.Many2one(
        comodel_name='product.category',
        string='Sales Category', help='Product category')
    sale_date = fields.Date(
        string='Sale Date', help='Help in Search customer which have matching sale order date.')
    sale_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Sale Item', help='Search customer based on sold items.')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """docstring for search"""
        sale_line_obj = self.env['sale.order.line']
        sale_obj = self.env['sale.order']
        partner_ids = []
        for val in args:
            if 'product_cat_id' in val:
                line_objs = sale_line_obj.search([('product_id.categ_id.name', val[1], val[-1])])
                for sale_line in line_objs:
                    if sale_line.order_partner_id.id not in partner_ids:
                        partner_ids.append(sale_line.order_partner_id.id)
            ## Checking for the date for particular sale order
            if 'sale_date' in val:
                sale_objs = sale_obj.search([('date_order', val[1], val[-1])])
                for sale_obj in sale_objs:
                    if sale_obj.partner_id.id not in partner_ids:
                        partner_ids.append(sale_obj.partner_id.id)
            ## checking for the product
            if 'sale_product_id' in val:
                line_objs = sale_line_obj.search([('product_id.name', val[1], val[-1])])
                for sale_line in line_objs:
                    if sale_line.order_partner_id.id not in partner_ids:
                        partner_ids.append(sale_line.order_partner_id.id)
        if partner_ids:
            args.append(['id', 'in', partner_ids])
        for val in args:
            if 'product_cat_id' in val:
                del args[args.index(val)]
            if 'sale_date' in val:
                del args[args.index(val)]
            if 'sale_product_id' in val:
                del args[args.index(val)]
        return super(ResPartber, self).search(args=args, offset=offset, limit=limit, order=order, count=count)


ResPartber()
