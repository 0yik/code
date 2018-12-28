from odoo import models, fields, api

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.depends('use_date', 'actual_bbd')
    def compute_bbd(self):
        for record in self:
            record.display_bbd = record.actual_bbd if record.actual_bbd else record.use_date

    @api.depends('batch_no', 'actual_batch_no')
    def compute_batch_no(self):
        for record in self:
            record.display_batch_no = record.actual_batch_no if record.actual_batch_no else record.batch_no

    batch_no = fields.Char('Batch No')
    actual_batch_no = fields.Char('Actual Batch No')
    display_batch_no = fields.Char(compute='compute_batch_no', string='Batch No')
    actual_bbd = fields.Datetime('Actual Before Before')
    display_bbd = fields.Datetime(compute='compute_bbd', string='Best before Date')

    def edit_batch_info(self, data_dict):
        self.ensure_one()
        try:
            vals = {}
            if data_dict.get('lot_name', False):
                vals['name'] = data_dict['lot_name']
            if data_dict.get('batch_no', False) and str(data_dict['batch_no']).lower() != 'false':
                if data_dict['batch_no'] == self.batch_no:
                    vals['actual_batch_no'] = False
                else:
                    vals['actual_batch_no'] = data_dict['batch_no']
            else:
                vals['batch_no'] = False
                vals['actual_batch_no'] = False
            if data_dict.get('bbd', False) and str(data_dict['bbd']).lower() != 'false':
                if self.use_date and data_dict['bbd'] == self.use_date[:10]:
                    vals['actual_bbd'] = False
                else:
                    vals['actual_bbd'] = data_dict['bbd'] + ' 00:00:00'
            else:
                data_dict['actual_bbd'] = False
                data_dict['use_date'] = False
            self.write(vals)
            return True
        except:
            return False


StockProductionLot()