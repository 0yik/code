from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
import time
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    business_unit_id = fields.Many2one('business.unit',string='Business Unit')
    mother_vessel= fields.Char('Mother Vessel')
    end_date = fields.Date(string="End Date")
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
        
    @api.multi
    def write(self, values):
        gantt_start_date = ''
        gantt_end_date = ''
        for laycan_record in self.laycan_ids:
            if laycan_record.commence_date and laycan_record.complete_date and self.start_date and self.end_date:
                if laycan_record.commence_date.split(' ')[0] == self.start_date.split(' ')[0] and laycan_record.complete_date.split(' ')[0] == self.end_date.split(' ')[0]:
                    laycan_record_update = laycan_record
                    gantt_start_date = values.get('start_date')
                    gantt_end_date = values.get('end_date')
        if gantt_start_date and gantt_end_date and self:
            laycan_record_update.write({'commence_date': gantt_start_date ,'complete_date': gantt_end_date})
        return super(SaleOrder,self).write(values)
        
    business_unit_id = fields.Many2one('business.unit',string='Business Unit', required=True)
    start_date = fields.Datetime(string='Start Date', store=True)
    end_date = fields.Datetime(string='End Date', store=True)
    
    @api.multi
    def action_confirm(self):
        res= super(SaleOrder, self).action_confirm()
        for so in self:
            laycan_ids = []
            gantt_start_date = False
            gantt_end_date = False
            if so.laycan_ids:
                for laycan_id in so.laycan_ids:
                    laycan_ids.append(laycan_id.id)
            if laycan_ids:
                max_laycan_id = max(laycan_ids)
                laycan_record = so.laycan_ids.browse(max_laycan_id)
                gantt_start_date = laycan_record.commence_date  
                gantt_end_date = laycan_record.complete_date
            so.start_date = gantt_start_date
            so.end_date= gantt_end_date
            
        return res
            
            
            
