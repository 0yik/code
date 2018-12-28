from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
import time
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    gantt_start_date = fields.Date(string="Gantt Start Date")
    gantt_end_date = fields.Date(string="Gantt End Date")
    end_date = fields.Date(string="End Date",)
    business_unit_id = fields.Many2one('business.unit',string='Business Unit')
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.has_key('gantt_pass') and self._context.has_key('gantt_pass') == True:
            self.env['sale.order'].with_context(gantt_pass=True).name_get()
        return super(StockPicking, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        
    @api.multi
    def write(self, fields):
        #print"\n write()",self._context
        gantt_start_date = ''
        gantt_end_date = ''
        if self._context.has_key('gantt_pass') and self._context.has_key('gantt_pass') == True:
            if self.business_unit_id:
                if self.business_unit_id.name == 'Ferry' or not self.gantt_start_date or not self.gantt_end_date:
                    raise UserError(_('Start date and End date in Work Order Can`t be edited.'))
                else:
                    for laycan_record in self.sale_order_id.laycan_ids:
                        if laycan_record.commence_date == self.gantt_start_date and laycan_record.complete_date == self.gantt_end_date:
                            laycan_record_update = laycan_record
                            gantt_start_date = fields.get('gantt_start_date')
                            gantt_end_date = fields.get('gantt_end_date')
                    #result = super(StockPicking, self).write(fields)
                    if gantt_start_date and gantt_end_date and self.sale_order_id:
                        laycan_record_update.write({'commence_date': gantt_start_date,'complete_date': gantt_end_date})
        return super(StockPicking, self).write(fields)
        
    #validity_date = fields.Date(String="Validity Date", related='sale_order_id.validity_date')

    # @api.depends('pack_operation_product_ids.qty_done')
    # def compute_end_date(self):
    #     for rec in self:
    #         for line in rec.pack_operation_product_ids:
    #             start_date = datetime.strptime(rec.min_date, DEFAULT_SERVER_DATETIME_FORMAT).date()
    #             end_date = datetime.strptime(rec.validity_date, DEFAULT_SERVER_DATE_FORMAT).date()
    #             to_do_qty = line.product_qty
    #             total_days = end_date - start_date
    #             rec.end_date = start_date + timedelta(days=(int(line.qty_done)))
'''
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    sale_order_id = fields.Many2one('sale.order','Sale Order')'''

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    #change so name in Stockpicking grant view
    @api.multi
    def name_get(self):
        #print"\n name_get()",self._context
        result = []
        for record in self:
            if self._context.has_key('gantt_pass') and self._context.get('gantt_pass') == True:
                if record.business_unit_id:
                    if record.business_unit_id.name == 'Ferry' or not record.mother_vessel:
                        result.append((record.id, record.name))
                    else:
                        result.append((record.id, record.mother_vessel))
                else:
                    result.append((record.id, record.name))
            else:
                result.append((record.id, record.name))
        #print"return name_get",result
        return result
        
    business_unit_id = fields.Many2one('business.unit',string='Business Unit', required=True)
    mother_vessel= fields.Char('Mother Vessel')
    
    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        picking_ids = self.env['stock.picking'].search([('group_id', '=', self.procurement_group_id.id)]) if self.procurement_group_id else []
        stock_picking_record = self.env['stock.picking'].search([('sale_order_id','=',self.id)], order='id desc', limit=1)
        date_order = self.date_order
        #if business_unit_id = Ferry
        if self.business_unit_id.name == "Ferry":
                gantt_start_date = date_order.split(' ')[0]  
                gantt_end_date = self.validity_date
                stock_picking_record.update({'gantt_start_date':gantt_start_date,
                                            'gantt_end_date':gantt_end_date,
                                            'business_unit_id':self.business_unit_id,})
                # if create delivery order                            
                if picking_ids:
                    for picking_id in picking_ids:
                        picking_id.update({'gantt_start_date':gantt_start_date,
                                             'gantt_end_date':gantt_end_date,
                                             'business_unit_id':self.business_unit_id,
                                             'sale_order_id':self.id,})
        #if business_unit_id != Ferry               
        elif self.laycan_ids:
            laycan_ids = []
            for laycan_id in self.laycan_ids:
                laycan_ids.append(laycan_id.id)
            max_laycan_id = max(laycan_ids)
            laycan_record = self.laycan_ids.browse(max_laycan_id)
            gantt_start_date = laycan_record.commence_date  
            gantt_end_date = laycan_record.complete_date  
            stock_picking_record.update({'gantt_start_date':gantt_start_date,
                                         'gantt_end_date':gantt_end_date,
                                         'business_unit_id':self.business_unit_id,})
            if picking_ids:
                for picking_id in picking_ids:
                    picking_id.update({'gantt_start_date':gantt_start_date,
                                         'gantt_end_date':gantt_end_date,
                                         'business_unit_id':self.business_unit_id,
                                         'sale_order_id':self.id,})
        return res
    
    @api.model
    def default_get(self, fields):
        rec = super(SaleOrder, self).default_get(fields)
        if self._context.get('default_requisition_id'):
            requisition_id = self._context.get('default_requisition_id')
            requisition_record = self.env['sale.requisition'].browse(requisition_id)
            rec.update({'business_unit_id':requisition_record.business_unit.id})
        return rec
        
                
class StockPickOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def write(self, vals):
        if vals.get('qty_done'):
            self.picking_id.end_date = fields.Date.today()
        return super(StockPickOperation, self).write(vals)    
