# -*- coding: utf-8 -*-
##############################################################################
#
#    DevIntelle Solution(Odoo Expert)
#    Copyright (C) 2015 Devintelle Soluation (<http://devintelle.com/>)
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
from openerp.exceptions import except_orm

from odoo import models, fields, api


class inventory_wizard(models.TransientModel):

    _name        = 'inventory.age.wizard'
    _description = 'Stock Aging Report'

    period_length       = fields.Integer('Period Length (days)', default=30)
    product_id          = fields.Many2one('product.product', 'Product')
    product_category_id = fields.Many2one('product.category', 'Product Category')
    warehouse_id        = fields.Many2one('stock.warehouse', 'Warehouse')
    location_id         = fields.Many2one('stock.location', 'Location')
    company_id          = fields.Many2one('res.company', 'Company')
    date_from           = fields.Date('Date', default=lambda *a: time.strftime('%Y-%m-%d'))

    def _print_report(self, data):
        res = {}

        period_length = data['form']['period_length']
        if period_length <= 0:
            raise except_orm(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise except_orm(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            res[str(i)] = {
                'name'  : (i != 0 and (str((5 - (i + 1)) * period_length) + '-' + str((5 - i) * period_length)) or ('+' + str(4 * period_length))),
                'stop'  : start.strftime('%Y-%m-%d'),
                'start' : (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)

        return self.env.get('report').get_action([], 'inventory_age_report.report_stockageing', data=data)


    @api.multi
    def check_report(self):
        data = {}
        data['ids'] = self._context.get('active_ids', [])
        data['model'] = self._context.get('active_model', 'ir.ui.menu')
        for record in self:
            data['form']  = self.read(['period_length', 'product_id', 'product_category_id', 'warehouse_id', 'location_id', 'company_id', 'date_from'])[0]
        return self._print_report(data)

    @api.model
    def get_lines(self, form):
        res = []

        quant_obj = self.env.get('stock.quant')
        product_category_id = form['product_category_id'][0]
        product_obj = self.env.get('product.product')
        products = product_obj.search([('categ_id', '=', product_category_id)])
        product_ids = products._ids
        if form.get('product_id', False) and form['product_id'][0] in product_ids:
            wizard_product_id = form['product_id'][0]
            product_ids = [wizard_product_id]
        for product in product_obj.browse(product_ids):
            product_dict = {
                'pname': product.name
            }
            location_id = form['location_id'][0]
            date_from = form['date_from']
            # warehouse = form['warehouse_id'][0]
            ctx = self._context.copy()
            ctx.update({
                'location': location_id,
                'from_date': date_from,
                'to_date': date_from
            })
            product_qty = product._product_available(False, False)
            qty_list = product_qty.get(product.id)
            product_dict.update({
                'onhand_qty' : qty_list['qty_available'],
            })
            for data in range(0, 6):
                total_qty = 0
                if form.get(str(data)):
                    start_date = form.get(str(data)).get('start')
                    stop_date = form.get(str(data)).get('stop')
                    if not start_date:
                        domain = [('in_date', '<=', stop_date), ('location_id', '=', location_id),
                                  ('product_id', '=', product.id)]
                    else:
                        domain = [('in_date', '<=', stop_date), ('in_date', '>=', start_date),
                                  ('location_id', '=', location_id), ('product_id', '=', product.id)]

                    for quant in quant_obj.search(domain):
                        total_qty += quant.qty
                    product_dict[str(data)] = total_qty
            res.append(product_dict)

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
