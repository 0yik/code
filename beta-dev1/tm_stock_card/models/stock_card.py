from odoo import models ,fields ,api
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class stock_card(models.Model):
    _name = 'stock.card'

    category_id     = fields.Many2one('category.main','Category')
    date_from       = fields.Date('Date From',default=fields.Date.today(),required=True)
    date_to         = fields.Date('Date To',default=fields.Date.today(),required=True)
    product_ids     = fields.Many2many('product.template',string='Products')
    category_subfirst_id = fields.Many2one('category.subfirst', string='Sub I')
    category_subsecond_id = fields.Many2one('category.subsecond', string='Sub II')
    product_brand_id = fields.Many2one('product.brand', string='Brand')
    branch_id = fields.Many2one('res.branch', string="Branch")
    branch = fields.Many2one('res.branch', string="Branch")

    @api.multi
    def stock_card_report_print(self):
	domain = []
        if self.category_id:
            domain.append(('category_main_id','=',self.category_id.id))
        if self.category_subfirst_id:
            domain.append(('category_subfirst_id','=',self.category_subfirst_id.id))
        if self.category_subsecond_id:
            domain.append(('category_subsecond_id','=',self.category_subsecond_id.id))
        if self.product_brand_id:
            domain.append(('product_brand_id','=',self.product_brand_id.id))
        self.product_ids = self.env['product.template'].search(domain)
        #self.product_ids = self.env['product.template'].search([('categ_id','=',self.category_id.id)])
        datas = {
            'doc_ids': self.ids,
            'doc_model': 'stock.card',
            'docs': self.read()[0]

        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'tm_stock_card.stock_card_report',
            'datas': datas
        }
class stock_card_report(models.AbstractModel):
    _name = 'report.tm_stock_card.stock_card_report'

    @api.multi
    def render_html(self, docids, data=None):
        report = self.env['report']._get_report_from_name('tm_stock_card.stock_card_report')
        stock_card = self.env['stock.card'].browse(docids)
        products = sorted(stock_card.product_ids)
        product_data = {}
        for product in products:
            product_line = []
            # lines           = self.env['stock.quant'].search([('product_id','=',product.product_variant_id.id or False),('in_date','>=',records.date_from),('in_date','<=',records.date_to)])
            sale_do         = self.env['stock.picking'].search([('sale_id', '!=', False),('branch_id','=',stock_card.branch_id.id)]).mapped('move_lines').filtered(lambda record:
                                     record.product_id.id == product.product_variant_id.id and
                                     datetime.datetime.strptime(record.date,DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT) >= stock_card.date_from and
                                     datetime.datetime.strptime(record.date, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT) <= stock_card.date_to)
            purchase_do     = self.env['stock.picking'].search([('purchase_id', '!=', False),('branch_id','=',stock_card.branch_id.id)]).mapped('move_lines').filtered(lambda record:
                                     record.product_id.id == product.product_variant_id.id and
                                     datetime.datetime.strptime(record.date,DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT) >= stock_card.date_from and
                                     datetime.datetime.strptime(record.date, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT) <= stock_card.date_to)
            sale_do1        = self.env['stock.picking'].search([('sale_id', '!=', False),('branch_id','=',stock_card.branch_id.id)]).mapped('move_lines').filtered(lambda record:
                                    record.product_id.id == product.product_variant_id.id and
                                    datetime.datetime.strptime(record.date, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT) < stock_card.date_from )
            purchase_do1    = self.env['stock.picking'].search([('purchase_id', '!=', False),('branch_id','=',stock_card.branch_id.id)]).mapped('move_lines').filtered(lambda record:record.product_id.id == product.product_variant_id.id and
                                        datetime.datetime.strptime(record.date, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT) < stock_card.date_from)
	    opening_data = self.env.cr.execute("SELECT h.product_template_id,SUM(h.quantity) FROM stock_history h, stock_move m WHERE h.move_id=m.id AND h.product_template_id in %s AND m.date < %s GROUP BY h.product_template_id",
                           (tuple([product.id]), stock_card.date_from + ' 00:00:00'))
            opening_data = self.env.cr.fetchall()
            qty = 0
            if opening_data:
                qty = opening_data[0][1]
            product_line.append({
                    'date'          : datetime.datetime.strptime(stock_card.date_from,DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y'),
                    'reference'     : 'O/B Opening Balance',
                    'unit'          : product.uom_id.name or '',
                    'masuk'         : qty,
                    'keluar'        : '',
                    'cost'          : '',
                    'saldo'         : (sum(purchase_do1.mapped('product_uom_qty')) - sum(sale_do1.mapped('product_uom_qty'))),
                    'cost3'         : '{0:,.2f}'.format(purchase_do1[0].price_unit) if purchase_do1 else 0 ,
                    'amount1'       : '',
                    'amount3'       : '{0:,.2f}'.format((sum(purchase_do1.mapped('product_uom_qty')) - sum(sale_do1.mapped('product_uom_qty')))*(purchase_do1[0].price_unit) if purchase_do1 else 0),
            })
            saldo = (sum(purchase_do1.mapped('product_uom_qty')) - sum(sale_do1.mapped('product_uom_qty')))

            for line in purchase_do:
                line_data = {
                    'date'          : datetime.datetime.strptime(line.date,DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d/%m/%Y'),
                    'reference'     : line.picking_id.name or '',
                    'unit'          : line.product_uom.name or '',
                    'masuk'         : line.product_uom_qty or 0,
                    'keluar'        : 0,
                    'cost'          : '{0:,.2f}'.format(line.price_unit * (line.price_unit * line.product_uom_qty)),
                    'cost3'         : '{0:,.2f}'.format(line.price_unit),
                    'saldo'         : saldo + line.product_uom_qty,
                    'amount1'       : '{0:,.2f}'.format(line.price_unit * line.product_uom_qty),
                    'amount3'       : '{0:,.2f}'.format(line.remaining_qty * line.price_unit),
                }
                saldo = saldo + line.product_uom_qty
                product_line.append(line_data)
            for line in sale_do:
                line_data = {
                    'date'      : datetime.datetime.strptime(line.date, DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d/%m/%Y'),
                    'reference' : line.picking_id.name or '',
                    'unit'      : line.product_uom.name or '',
                    'masuk'     : 0,
                    'keluar'    : line.product_uom_qty or 0,
                    'cost'      : '{0:,.2f}'.format(line.product_uom_qty * (line.price_unit * line.product_uom_qty)),
                    'cost3'     : '{0:,.2f}'.format(line.price_unit),
                    'saldo'     : saldo - line.product_uom_qty,
                    'amount2'   : '{0:,.2f}'.format(line.price_unit * line.product_uom_qty),
                    'amount3'   : '{0:,.2f}'.format(line.remaining_qty * line.price_unit)
                }
                saldo = saldo - line.product_uom_qty
                product_line.append(line_data)
            product_data.update({product.id:product_line})
        docargs = {'doc_ids'    : docids,
                   'doc_model'  : report.model,
                   'data'       : data,
                   'docs'       : stock_card,
                   'products'   : products,
                   'product_data': product_data,
                   }
        return self.env['report'].render('tm_stock_card.stock_card_report', docargs)

