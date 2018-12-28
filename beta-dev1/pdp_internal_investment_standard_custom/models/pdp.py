from odoo import api, fields, models, _,exceptions
import base64
from xlrd import open_workbook
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_standard_id = fields.Many2one('stock.standard')

    def default_get(self, fields):
        res = super(StockPicking, self).default_get(fields)
        StockMove = self.env['stock.move']
        context = self._context or {}
        active_model = context.get('active_model', False)
        active_ids = context.get('active_ids', False)
        ids = []
        val=[]
        v=''
        res['move_lines'] = ''
        if (active_model or active_ids) and active_model == 'stock.standard':
            StockStandard = self.env[active_model].browse(active_ids)
            res.update({
                'picking_type_id': StockStandard.picking_type_id and StockStandard.picking_type_id.id or False,
                'location_dest_id': StockStandard.location_id and StockStandard.location_id.id or False,
                'state': 'draft',
                'stock_standard_id': StockStandard.id,
                'location_id' : StockStandard.location_id.id,
            })
            for line in StockStandard.stock_standard_line:
                if(line.to_do_amount != False):
                    v= [0, 0, {
                            'product_id' : line.product_id.id,
                            'code' : line.product_id_code,
                            'product_uom_qty' : line.to_do_amount,
                            'product_uom' : line.product_id.uom_id.id,
                            'location_id' : line.warehouse_id and line.warehouse_id.id or False,
                            'location_dest_id': StockStandard.location_id and StockStandard.location_id.id or False,
                            'scrapped' : True,
                            'state' : 'draft',
                            'date_expected' : datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                    }]
                    val.append([v])
       
                    res['move_lines'] = val
        
        return res


class Employee(models.Model):
    _inherit = "stock.standard"
    
    warehouse = fields.Many2one('stock.location',string="Warehouse")
    file = fields.Binary(string='BOM File', required=True)
    file_name = fields.Char('File Name')
    file_type = fields.Char('File Type')
    
    
    
    @api.onchange('picking_type_id')
    def picking_warehouse(self):
        self.warehouse = self.picking_type_id.default_location_src_id
    

    def import_product(self):
        return {'type': 'ir.actions.act_window',
                'name': 'hr.file.form' ,
                'res_model': 'hr.file',
                'view_mode': 'form',
                'target': 'new',
               
                }


class stockt_standard_line(models.Model):
    _inherit = 'stock.standard.line'

    @api.depends('stock_standard_id.location_id','product_id')
    @api.multi
    def compute_qty_of_product(self):
        
        for r in self:
            BC = r.investment_standard_amount - r.stock_current_shop_amount
            if(BC > r.stock_warehouse_amount ):
                r.to_do_amount = r.stock_warehouse_amount
            else:
                r.to_do_amount = BC
        
class Filing(models.Model):
    _name = "hr.file"    
    file = fields.Binary(string='Upload File')
    file_name = fields.Char('File Name')
    file_type = fields.Char('File Type')
    typee_format = fields.Selection([('csv','CSV File'),
                                     ('xls','XLS File')
                                     
                                     ],string="Upload File",default='csv')
    
    @api.multi
    def _addfromfile(self,val,stock):
        length = len(val)
        lst= []
        dataloaded=[]
        for i in range(length):
            
            
                lst.append(val[i].split(','))
         
        print(lst)
        data = self.env['product.product'].search([('name','=',lst[0][1]),('code','=',lst[0][0])])
        for i in data:   
            pass
            if(i.code != False and i.id != False):
                val = [0,0,{'product_id_code':i.code,
                       'product_id':i.id
                    }]
                
                dataloaded.append(val)
                
        stock.write({'stock_standard_line':dataloaded})

    
    @api.multi
    def import_csv(self, options):
        """ Returns a CSV-parsed iterator of all empty lines in the file
            :throws csv.Error: if an error is detected during CSV parsing
            :throws UnicodeDecodeError: if ``options.encoding`` is incorrect
        """
        stock = self.env['stock.standard'].search([('id','=',options['active_id'])])
        csv_data = self.file
        file_type = self.file_name.split(".")
        if(self.location_id != False and self.picking_type_id != False and self.warehouse != False):
            if(file_type[1] == 'csv'):
                self.typee_format= 'csv'
            elif(file_type[1] == 'xlsx' or file_type[1] == 'xls'):
                self.typee_format= 'xls'
    #         csv
            if(file_type[1] == 'csv' and self.typee_format== 'csv'):
                
                csv_data = base64.decodestring(self.file).decode(encoding='utf-8')
                self._addfromfile(csv_data.split('\n'),stock)
    #         xls
    
            elif((file_type[1] == 'xlsx' or file_type[1] == 'xls') and self.typee_format== 'xls'):
                
                file_data = self.file.decode('base64')
                wb = open_workbook(file_contents=file_data)
                newar = []
                data = []
                data_rows = []
                
                dataloaded=[]
               
                for s in wb.sheets():
                    for row in range(s.nrows):
                        dd = []
                        for col in range(s.ncols):
                            value = (s.cell(row, col).value)
                            dd.append(value)
                        data_rows.append(dd)
                            
                for data_row in data_rows:
                    if(isinstance(data_row[0], int) or isinstance(data_row[0], float)):
                        ln_of_code = str(int(data_row[0]))
            #                         ln_of_code = len(str(int(data_row[0])))
                        code = ln_of_code.zfill(8)
                    
                        data = self.env['product.product'].search([('name','=',data_row[1]),('code','=',code)])
                    
                    if(data):
                        newar.append(data)
                for n in newar:
                    pass
                    for i in n:
                        if(i.code != False and i.id != False):
                            val = [0,0,{'product_id_code':i.code,
                                   'product_id':i.id
                                }]
                            
                            dataloaded.append(val)
                
                stock.write({'stock_standard_line':dataloaded})
            else:
                raise exceptions.Warning(_("Invalid Extension of File. Select Either .Xls or .CSV File"))
        else:
            raise exceptions.Warning(_("Fill Picking Id, Location, WareHouse first"))
        
        
