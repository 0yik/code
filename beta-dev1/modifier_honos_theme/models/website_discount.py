# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class WebsiteDiscount(models.Model):
    _name = 'website.discount'

    name = fields.Char('Title', required=True)
    description = fields.Text('Description')
    image = fields.Binary('Image')
    # discount_for = fields.Selection([('sale', 'Sale'), ('rent', 'Rent'), ('both', 'Both (Sale & Rent)')], required=True) # now discount applied only rent
    discount = fields.Float('Discount (%)', required=True)
    applied_on = fields.Selection([('product', 'Product'), ('category', 'Category')], required=True)
    all_products = fields.Boolean()
    category_id = fields.Many2one('product.public.category')
    product_ids = fields.Many2many('product.template', 'website_discount_product_rel', string="Products")
    sequence = fields.Integer()
    start_datetime = fields.Datetime("Start Datetime", required=True)
    end_datetime = fields.Datetime("End Datetime", required=True)
    active = fields.Boolean(default=True)
    # pricelist_id = fields.Many2one('product.pricelist', ondelete="cascade") # no discount on sale then no pricelist

    @api.constrains('start_datetime', 'end_datetime')
    def _constrains_start_end_datetime(self):
        for record in self:
            if record.end_datetime <= record.start_datetime:
                raise ValidationError(_('Ending Datetime cannot be set before Starting Datetime.'))

    @api.constrains('discount')
    def _constrains_discount(self):
        for record in self:
            if record.discount <= 0:
                raise ValidationError(_('Discount cannot be less than or equal to 0.'))

    _sql_constraints = [
        ('check_discount_period', 'CHECK(end_datetime > start_datetime)', 'Error ! Ending Datetime cannot be set before Starting Datetime.'),
        ('check_discount', 'CHECK(discount > 0)', 'Error ! Discount cannot be less than or equal to 0.')
    ]

    def check_overlap(self, new_start, new_end):
        if new_start and new_end:
            all_records = self.env['website.discount'].search([]) - self
            for record in all_records:
                if (record.start_datetime < new_end and record.end_datetime > new_start):
                    raise UserError(_('Error ! Dates are overlapping.'))

    def update_vals(self, values):
        if values.get('applied_on') == 'product':
            values['category_id'] = None
        elif values.get('applied_on') == 'category':
            values['all_products'] = False
            values['product_ids'] = [(5, 0, 0)]
        elif values.get('all_products'):
            values['product_ids'] = [(5, 0, 0)]

    # def set_pricelist(self):
    #     for record in self:
    #         date_start = fields.Date.to_string(fields.Date.from_string(record.start_datetime))
    #         date_end = fields.Date.to_string(fields.Date.from_string(record.end_datetime))
    #         vals = {'name': record.name}
    #         if record.applied_on == 'product':
    #             if record.all_products:
    #                 vals['item_ids'] = [(0, 0, {
    #                     'applied_on': '3_global',
    #                     'date_start': date_start,
    #                     'date_end': date_end,
    #                     'compute_price': 'percentage',
    #                     'percent_price': record.discount
    #                 })]
    #             else:
    #                 vals['item_ids'] = []
    #                 items = {
    #                     'applied_on': '1_product',
    #                     'compute_price': 'percentage',
    #                     'percent_price': record.discount,
    #                     'date_start': date_start,
    #                     'date_end': date_end,
    #                 }
    #                 for product in record.product_ids:
    #                     val = items.copy()
    #                     val['product_tmpl_id'] = product.id
    #                     vals['item_ids'].append((0, 0, val))
    #         if record.applied_on == 'category':
    #             vals['item_ids'] = []
    #             items = {
    #                 'applied_on': '1_product',
    #                 'compute_price': 'percentage',
    #                 'percent_price': record.discount,
    #                 'date_start': date_start,
    #                 'date_end': date_end,
    #             }

    #             public_categs = self.env['product.public.category'].search([('id', 'child_of', record.category_id.id)])
    #             rel_table = self.env['ir.model.fields'].search([('model', '=', 'product.template'), ('name', '=', 'public_categ_ids')])
    #             query = 'select ' + rel_table.column1 + ' from ' + rel_table.relation_table + ' where ' + rel_table.column2 + ' IN %s'
    #             self.env.cr.execute(query, (tuple(public_categs.ids),))
    #             match_recs = self.env.cr.dictfetchall()
    #             product_ids = []
    #             if match_recs:
    #                 product_ids = [m['product_template_id'] for m in match_recs]
    #             for product in product_ids:
    #                 val = items.copy()
    #                 val['product_tmpl_id'] = product
    #                 vals['item_ids'].append((0, 0, val))

    #         if record.pricelist_id:
    #             record.pricelist_id.write({'item_ids': [(5, 0, 0)]})
    #             record.pricelist_id.write(vals)
    #         else:
    #             pricelist = self.env['product.pricelist'].create(vals)
    #             record.pricelist_id = pricelist.id

    @api.model
    def create(self, values):
        self.check_overlap(values.get('start_datetime'), values.get('end_datetime'))
        self.update_vals(values)
        discount = super(WebsiteDiscount, self).create(values)
        # discount.set_pricelist()
        return discount

    @api.multi
    def write(self, values):
        for record in self:
            if 'start_datetime' in values or 'end_datetime' in values:
                record.check_overlap(values.get('start_datetime') or record.start_datetime, values.get('end_datetime') or record.end_datetime)
        self.update_vals(values)
        discount = super(WebsiteDiscount, self).write(values)
        # self.set_pricelist()
        return discount

    def copy(self, default=None):
        raise UserError(_('Duplicate operation is not allowded.'))

    def _get_currrent_offer(self):
        now = fields.Datetime.now()
        rec = self.env['website.discount'].sudo().search([('start_datetime', '<=', now), ('end_datetime', '>=', now)], limit=1)
        return rec

    def _cron_set_rent_discount_on_product(self):
        ProductTemplate = self.env['product.template']
        rec = self._get_currrent_offer()
        if rec:
            products = self.env['product.template']
            if rec.applied_on == 'product':
                products = rec.all_products and ProductTemplate.search([]) or rec.product_ids
            if rec.applied_on == 'category':
                public_categs = self.env['product.public.category'].search([('id', 'child_of', rec.category_id.id)])
                rel_table = self.env['ir.model.fields'].search([('model', '=', 'product.template'), ('name', '=', 'public_categ_ids')])
                query = 'select ' + rel_table.column1 + ' from ' + rel_table.relation_table + ' where ' + rel_table.column2 + ' IN %s'
                self.env.cr.execute(query, (tuple(public_categs.ids),))
                match_recs = self.env.cr.dictfetchall()
                if match_recs:
                    product_ids = [m['product_template_id'] for m in match_recs]
                    products = ProductTemplate.browse(product_ids)
            if products:
                products.write({'rent_disc_available': True, 'rent_disc': rec.discount})
            (ProductTemplate.search([]) - products).write({'rent_disc_available': False, 'rent_disc': 0})
        else:
            ProductTemplate.search([]).filtered(lambda p: p.rent_disc_available).write({'rent_disc_available': False, 'rent_disc': 0})
