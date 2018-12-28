from odoo import api, fields, models, _


class SaleOrderReportLabo(models.TransientModel):

    _name = 'sale.order.report.labo'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    order_from = fields.Many2one('sale.order', 'Sale Order From')
    order_to = fields.Many2one('sale.order', 'Sale Order To')

    @api.multi
    def print_report_labo(self):
        data = {}
        sale_order_obj = self.env['sale.order']
        sale_date_rec = sale_order_obj.search([('date_order','>=', self.date_from),
                                               ('date_order','<=', self.date_to)])
        if self.order_from and self.order_to:
            sale_order_rec = sale_order_obj.search([('id', '>=', self.order_from.id),
                                                    ('id', '<=', self.order_to.id)])
        else:
            sale_order_rec = False
        if sale_date_rec and sale_order_rec:
            order_rec = sale_order_obj.browse(list(set(sale_order_rec.ids + sale_date_rec.ids)))
            data.update({'order': sorted(order_rec.ids)})
            return self.env['report'].get_action([], 'laborindo_report_sales_order.sale_report_labo', data=data)
        elif sale_date_rec:
            data.update({'order': sorted(sale_date_rec.ids)})
            return self.env['report'].get_action([], 'laborindo_report_sales_order.sale_report_labo', data=data)
