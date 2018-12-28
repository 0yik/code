from odoo import models, fields, api
from datetime import datetime as date
from odoo.exceptions import UserError
import calendar
import odoo.addons.decimal_precision as dp
from odoo.tools import float_round

# wizard model for customer or warehouse report
class custom_wizard(models.TransientModel):
    _name = 'custom.wizard'
    _description = "custom Wizard"
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner', string='Customer')
    stock_warehouse_id = fields.Many2one(
        'stock.warehouse', string="Stock Warehouses")
    start_date = fields.Date(
        string="Start Date", required=True, default=date.today().replace(day=1))
    end_date = fields.Date(string="End Date", required=True, default=date.today(
    ).replace(day=calendar.monthrange(date.today().year, date.today().month)[1]))
    select_report = fields.Selection([('customer', 'product by customer'), ('warehouse', 'product by warehouse')],
                                     string='Select Report', required=True, default="warehouse")

    # set the select_report selection field
    @api.model
    def default_get(self, vals):
        default_get_res = super(custom_wizard, self).default_get(vals)
        for i in vals:
            if i == 'partner_id':
                default_get_res.update({'select_report': 'customer'})
            else:
                default_get_res.update({'select_report': 'warehouse'})
        return default_get_res

    # submit button for warehouse or customer report
    @api.multi
    def submit_information(self):
        if self.partner_id.id :
            context = {'group_by_no_leaf': 1,
                       'search_default_partner_id': self.partner_id.id,
                       'group_by': ['partner_id', 'product_id','name' ],
                       'start_date': self.start_date, 'end_date': self.end_date
                       }
            domain = [('partner_id', 'in', [self.partner_id.id] + [i.id for i in self.partner_id.child_ids]),
                      ('date', '>=', self.start_date),
                      ('date', '<=', self.end_date)
                      ]
        elif  self.stock_warehouse_id.id:
            context = {'group_by_no_leaf': 1,
                        'search_default_warehouse_id': self.stock_warehouse_id.id,
                       'group_by': ['warehouse_id', 'product_id','name' ],
                       'start_date': self.start_date, 'end_date': self.end_date
                       }
            domain = [('warehouse_id', '=', self.stock_warehouse_id.ids),
                      ('date', '>=', self.start_date),
                      ('date', '<=', self.end_date)
                      ]
        elif self.select_report == 'customer' :
            domain = ['|',
                      ('date', '>=', self.start_date),
                      ('date', '<=', self.end_date),
                      ]
            context = {'group_by_no_leaf': 1,
                       'group_by': ['partner_id', 'product_id','name']
                       }
        elif self.select_report == 'warehouse':
            domain = ['|',
                      ('date', '>=', self.start_date),
                      ('date', '<=', self.end_date),
                      ]
            context = {'group_by_no_leaf': 1,
                       'group_by': ['warehouse_id','product_id','name']
                       }   
        return {
            'name': 'custom reports',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'pivot',
            'res_model': 'sale.report',
            'view_id': '',
            'help': '''This report performs analysis on your quotations and sales orders. Analysis check your sales revenues and sort it by different group criteria (salesman, partner, product, etc.) Use this report to perform analysis on sales not having invoiced yet. If you want to analyse your turnover, you should use the Invoice Analysis report in the Accounting application.''',
            'context': context,
            'domain': domain
        }
#graph view details
    @api.multi
    def submit_graph(self):
        if self.partner_id.id :
            context = {'group_by_no_leaf': 1,
                       'search_default_partner_id': self.partner_id.id,
                       'group_by': ['partner_id', 'product_id','name' ],
                       'start_date': self.start_date, 'end_date': self.end_date
                       }
            domain = [('partner_id', 'in', [self.partner_id.id] + [i.id for i in self.partner_id.child_ids]),
                      ('date', '>=', self.start_date),
                      ('date', '<=', self.end_date)
                      ]
        elif  self.stock_warehouse_id.id:
            context = {'group_by_no_leaf': 1,
                        'search_default_warehouse_id': self.stock_warehouse_id.id,
                       'group_by': ['warehouse_id', 'product_id','name' ],
                       'start_date': self.start_date, 'end_date': self.end_date
                       }
            domain = [('warehouse_id', '=', self.stock_warehouse_id.ids),
                      ('date', '>=', self.start_date),
                      ('date', '<=', self.end_date)
                      ]
        elif self.select_report == 'customer' :
            domain = ['|',
                      ('date', '>=', self.start_date),
                      ('date', '<=', self.end_date),
                      ]
            context = {'group_by_no_leaf': 1,
                       'group_by': ['partner_id', 'product_id','name']
                       }
        elif self.select_report == 'warehouse':
            domain = ['|',
                      ('date', '>=', self.start_date),
                      ('date', '<=', self.end_date),
                      ]
            context = {'group_by_no_leaf': 1,
                       'group_by': ['warehouse_id','product_id','name']
                       }   
        return {
            'name': 'custom reports',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'graph',
            'res_model': 'sale.report',
            'view_id': '',
            'help': '''This report performs analysis on your quotations and sales orders. Analysis check your sales revenues and sort it by different group criteria (salesman, partner, product, etc.) Use this report to perform analysis on sales not having invoiced yet. If you want to analyse your turnover, you should use the Invoice Analysis report in the Accounting application.''',
            'context': context,
            'domain': domain
        }

    # common method for print pdf or xls file
    def report_data(self):
        data = {}
        precision = self.env.user.company_id.currency_id.decimal_places
        if self.select_report == "customer":
            if self.partner_id:
                report_data = []
                product_data = []
                sales_ids = self.env['sale.report'].search(
                    [('partner_id', 'in', [self.partner_id.id] + [i.id for i in self.partner_id.child_ids]),
                     
                     ('date', '>=', self.start_date),
                     ('date', '<=', self.end_date), ('product_uom_qty', '>', 0)])
                
                if sales_ids:
                    
                    for sale in sales_ids:
                        bill_amount =  gross_price =margin = 0.0
                        bill_amount =  sale.price_unit *  sale.product_uom_qty
                        gross_price = sale.product_uom_qty * (sale.price_unit- sale.purchase_price)
                        margin = 100 * ( gross_price / bill_amount)  
                        
                        product_data.append({'code' : sale.product_id.default_code ,'product_name': sale.product_id.name , 
                                             'qty': sale.product_uom_qty,
                                             'uom':  sale.product_uom.name,
                                             'bill_amount':  bill_amount,
                                             'sale_price':  sale.price_unit,
                                         'cost_price':sale.purchase_price ,'gross_profit':gross_price,
                                         'ref': sale.name,
                                         'margin': float_round(margin, precision_digits=precision) })
                if product_data:
                    report_data.append({'customer': self.partner_id.name,'product_data':product_data,'partner':True })
                        
                else:
                    raise UserError(
                        'There is no data to display for this partner.')
            else:
                report_data = []
                partner_ids = self.env['res.partner'].search([])
                for partner in partner_ids:
                    sales_ids = self.env['sale.report'].search(
                        [('partner_id', 'in', [partner.id] + [i.id for i in partner.child_ids]),
                         ('date', '>=', self.start_date),
                         ('date', '<=', self.end_date), ('product_uom_qty', '>', 0)])
                    product_data = []
                   
                    if sales_ids:
                        for sale in sales_ids:
                            bill_amount =  gross_price = margin = 0.0
                            bill_amount =  sale.price_unit *  sale.product_uom_qty
                            gross_price = sale.product_uom_qty * (sale.price_unit- sale.purchase_price)
                            margin = 100 * ( gross_price / bill_amount)  
                            
                            product_data.append({'code' : sale.product_id.default_code ,'product_name': sale.product_id.name , 
                                                 'qty': sale.product_uom_qty,
                                                 'uom':  sale.product_uom.name,
                                                 'bill_amount':  bill_amount,
                                                 'sale_price':  sale.price_unit,
                                                 'ref': sale.name,
                                                 'cost_price':sale.purchase_price ,'gross_profit':gross_price,
                                                 'margin': float_round(margin, precision_digits=precision) })
                    if product_data:
                        report_data.append({'customer': partner.name,'product_data':product_data ,'partner':True})

        elif self.select_report == "warehouse":
            data['form'] = self.read(
                ['start_date', 'end_date', 'stock_warehouse_id', 'select_report'])[0]
                
            if self.stock_warehouse_id:
                report_data = []
                product_data = []
                self.env.cr.execute(''' select sr.product_id ,sr.price_unit ,sum(product_uom_qty) as qty,
                    pt.name as product_name,
                    pt.default_code as code,
                    po.name as uom,
                    sum(sr.price_unit * sr.product_uom_qty) as bill_amount ,
                    coalesce(sr.purchase_price,0) as cost_price,
                    ((sr.price_unit - coalesce(sr.purchase_price ,0) ) * sum(product_uom_qty)) as gross_profit,
                    coalesce((100 * ( (sr.price_unit - coalesce(sr.purchase_price,0) ) / sr.price_unit )),0) as margin
                    from sale_report sr
                    join product_product pp on sr.product_id = pp.id
                    join product_template pt on  pp.product_tmpl_id =pt.id
                    join product_uom po on pt.uom_id=po.id
                    where sr.warehouse_id = %s and  (date_trunc('day', date) between %s and 
                    %s) group by sr.product_id ,sr.price_unit ,pt.name,pt.default_code,po.name,sr.purchase_price''', (self.stock_warehouse_id.id,self.start_date,self.end_date))
                results = self.env.cr.dictfetchall()
                for r in results:
                    if r.get('code') == None :
                        r['code']  = ''
                    if r.get('bill_amount') == None :
                        r['bill_amount']  = 0.0
                    if r.get('cost_price') == None :
                        r['cost_price']  = 0.0
                    if r.get('gross_profit') == None :
                        r['gross_profit']  = 0.0
                    if r.get('margin') == None :
                        r['margin']  = 0.0
                    if r.get('sale_price') == None :
                            r['sale_price']  = 0.0
                        
                    product_data.append({'code' : r.get('code') ,
                                         'product_name': r.get('product_name') ,
                                          'qty': r.get('qty'),
                                          'bill_amount':  float_round(r.get('bill_amount'),precision_digits=precision),
                                         'cost_price':float_round(r.get('cost_price') ,precision_digits=precision),
                                        'gross_profit':float_round(r.get('gross_profit'),precision_digits=precision) ,
                                         'margin': float_round( r.get('margin'), precision_digits=precision),
                                         'uom':r.get('uom'), 
                                         'sale_price': r.get('price_unit') })
                if product_data:
                    report_data.append({'warehouse' : self.stock_warehouse_id.name , 'product_data': product_data})
                if not results:
                    raise UserError(
                        'There is no data to display for this warehouse.')
            else:
                report_data = []
                warehouse_ids = self.env['stock.warehouse'].search([])
                for warehouse in warehouse_ids:
                    product_data = []
                    self.env.cr.execute(''' select sr.product_id ,sr.price_unit,sum(product_uom_qty) as qty,
                        pt.name as product_name,
                        pt.default_code as code,
                        po.name as uom,
                        sum(sr.price_unit * sr.product_uom_qty) as bill_amount ,
                        coalesce(sr.purchase_price,0) as cost_price,
                        ((sr.price_unit - coalesce(sr.purchase_price ,0) ) * sum(product_uom_qty))  as gross_profit,
                        coalesce((100 * ( (sr.price_unit - coalesce(sr.purchase_price,0) ) / sr.price_unit )),0) as margin
                        from sale_report sr
                        join product_product pp on sr.product_id = pp.id
                        join product_template pt on  pp.product_tmpl_id =pt.id
                        join product_uom po on pt.uom_id=po.id
                        where sr.warehouse_id = %s and  (date_trunc('day', date) between %s and 
                        %s) group by sr.product_id ,sr.price_unit ,pt.name,pt.default_code,po.name,sr.purchase_price''', (warehouse.id,self.start_date,self.end_date))
                    results = self.env.cr.dictfetchall()
                    for r in results:
                        if r.get('code') == None :
                            r['code']  = ''
                        if r.get('bill_amount') == None :
                            r['bill_amount']  = 0.0
                        if r.get('cost_price') == None :
                            r['cost_price']  = 0.0
                        if r.get('gross_profit') == None :
                            r['gross_profit']  = 0.0
                        if r.get('margin') == None :
                            r['margin']  = 0.0
                        if r.get('sale_price') == None :
                            r['sale_price']  = 0.0
                        product_data.append({'code' : r.get('code') ,
                                             'product_name': r.get('product_name') ,
                                              'qty': r.get('qty'),
                                            'bill_amount':  float_round(r.get('bill_amount'),precision_digits=precision),
                                            'cost_price':float_round(r.get('cost_price') ,precision_digits=precision),
                                            'gross_profit':float_round(r.get('gross_profit'),precision_digits=precision) ,
                                             'margin': float_round( r.get('margin'), precision_digits=precision),
                                             'uom':r.get('uom'), 
                                             'sale_price': r.get('price_unit') })
                    if product_data:
                        report_data.append({'warehouse' : warehouse.name , 'product_data': product_data})
        return report_data
    
    #  method for pdf print button
    def print_report(self):
        data = {}
        data['form'] = self.read(
            ['start_date', 'end_date', 'select_report'])[0]
            
        data['form']['reports'] = self.report_data()
        return self.env['report'].get_action(self,'itmcs_statistical_reports.report_salereport', data=data)

    #  method for xls download button
    
    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        ctx =self.report_data()
        user = self.env["res.users"].browse(self._uid)
        company_name = user.company_id.name
        header_bgcolor = user.company_id.company_header_bgcolor
        header_fontcolor = user.company_id.company_header_fontcolor
        report_header_bgcolor = user.company_id.report_header_bgcolor
        report_header_fontcolor = user.company_id.report_header_fontcolor
        title_bgcolor = user.company_id.title_bgcolor
        title_fontcolor = user.company_id.title_fontcolor
        subtitle_bgcolor = user.company_id.subtitle_bgcolor
        subtitle_fontcolor = user.company_id.subtitle_fontcolor
        text_bgcolor = user.company_id.text_bgcolor
        text_fontcolor = user.company_id.text_fontcolor
        datas['model'] = 'custom.wizard'
        datas['form'] =self.read(
            ['start_date', 'end_date', 'select_report'])[0]
        datas['form']['context'] = ctx
        datas['form']['company'] = company_name
        datas['form']['company_header_bgcolor'] = header_bgcolor
        datas['form']['company_header_fontcolor'] = header_fontcolor
        datas['form']['report_header_bgcolor'] = report_header_bgcolor
        datas['form']['report_header_fontcolor'] = report_header_fontcolor
        datas['form']['title_bgcolor'] = title_bgcolor
        datas['form']['title_fontcolor'] = title_fontcolor
        datas['form']['subtitle_bgcolor'] = subtitle_bgcolor
        datas['form']['subtitle_fontcolor'] = subtitle_fontcolor
        datas['form']['text_bgcolor'] = text_bgcolor
        datas['form']['text_fontcolor'] = text_fontcolor
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'itmcs_statistical_reports.sales_analysis.xlsx',
                    'datas': datas,
                    'name': 'Custom sale reports'
                    }


class SaleReport(models.Model):
    _inherit = "sale.report"
    
    
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    purchase_price = fields.Float('Cost Price', required=True, digits=dp.get_precision('Cost Price'), default=0.0)
    gross_profit= fields.Float('Gross Profit', required=True, digits=dp.get_precision('Gross profit'), default=0.0)
    margin_per = fields.Float('Margin %', required=True, digits=dp.get_precision('Margin %'), default=0.0)

    def _select(self):
        select = super(SaleReport, self)._select()
        select += """
       ,sum(l.price_unit) as price_unit ,sum(l.purchase_price) as purchase_price , 
       (  (((l.price_unit - coalesce(l.purchase_price ,0) ) * sum(product_uom_qty))/ (l.price_unit * sum(product_uom_qty) ) )* 100 ) as margin_per, 
       ((l.price_unit - coalesce(l.purchase_price ,0) ) * sum(product_uom_qty))  as gross_profit
        """
        return select

    def _group_by(self):
        group_by_str = super(SaleReport, self)._group_by()
        group_by_str += """
         ,l.price_unit,l.purchase_price
        """
        return group_by_str
