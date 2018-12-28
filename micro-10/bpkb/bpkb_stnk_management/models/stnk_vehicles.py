from odoo import api, fields, models, _
import time
import datetime 
from datetime import datetime
from odoo.exceptions import UserError

class STNKVEHICLES(models.Model):
    _name = "stnk.vehicles"
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('active', 'Active'),
        ('stop', 'Stopped'),
        
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    
    
    name=fields.Char("Description")
    nr = fields.Char('Nomor Registrasi')
    np= fields.Char('Nama Pemilik')
    mt= fields.Char('Merek / Type')
    jm= fields.Selection([
        ('mb', 'Minibus'),
        ('mob','Mobil'),
        ('kereta,','Kereta,'),
        ('truk)','Truk)'),
        ],
        string ='Jenis / Model')
    tp= fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'Tahun Pembuatan')
    tpera= fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'Tahun Perakitan')
    tahun_terbit = fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'Tahun Terbit')
    berlaku_sampai = fields.Datetime("Berlaku Sampai")
    
    nmor= fields.Char('Nomor')
    npbkb= fields.Char('No BPKB')
    bahanbakar= fields.Char('Bahan Bakar')
    warna_tnkb= fields.Char('Warna TNKB')
    kepemilikanke= fields.Char('Kepemilikan ke')
    noregistrasilama= fields.Char('No Registrasi Lama')
    kodenjkb= fields.Char('Kode NJKB')
    nourut= fields.Char('No Urut')
    nik= fields.Char('NIK:')
    nohp= fields.Char('No HP')
    pp= fields.Char('Penaksir Pajak')
    kasir = fields.Char('Kasir')
    dt = fields.Date('Ditetapkan tanggal')
    stnk_list = fields.One2many('stnk.vehicles.line','sl_id',string="List")
    
    def confirm(self):
        self.write({'state':'active'})
        
    def stop(self):
        self.write({'state':'stop'})
        
    def reset_to_draft(self):
        self.write({'state':'draft'})
        
    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    
    @api.multi
    def unlink(self):
        for order in self:
            if order.state  in ('active','stop'):
                raise UserError(_('You can not delete a record once it is Active or Stopped! Try to Reset it .'))
        return super(STNKVEHICLES, self).unlink()
#     @api.multi
#     def load(self):
#         sntk_tab = self.env['stnk.vehicles.table'].search([])
#         for s in sntk_tab:
#             self.stnk_list.write({'name': s.name})
    @api.depends('stnk_list.jumlah','stnk_list.sanskiadministrasi','stnk_list.pokok')
    def _amount_all(self):
        print('yyyyy')
        pass
        pass
          

class STNKVEHICLESTABLE(models.Model):   
    _name = "stnk.vehicles.table"
    
    
#     sl_id= fields.Many2one('stnk.vehicles')
    name=fields.Char("Name")
    
class STNKVEHICLESLine(models.Model):
    _name = "stnk.vehicles.line"
    
    
#     slt_id= fields.Many2one('stnk.vehicles.table',string="Name")
    sl_id= fields.Many2one("stnk.vehicles")
#     name=fields.Char()
    jumlah = fields.Float('Jumlah')
    sanskiadministrasi = fields.Float('Sanski Administrasi')
    pokok= fields.Float('Pokok')
    
    slt_id= fields.Many2one('stnk.vehicles.table',string="Name")    

class product_template(models.Model):
    
    _inherit = "product.template"
    
    stnk_id = fields.Many2one("stnk.vehicles",string="STNK")
    