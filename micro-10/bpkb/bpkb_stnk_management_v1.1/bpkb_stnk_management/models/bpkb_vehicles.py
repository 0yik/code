from odoo import api, fields, models, _
import time
import datetime 
from datetime import datetime
from odoo.exceptions import UserError

class bpkb_vehicles_class(models.Model):
    _name = 'bpkb.vehicles'

    # fields for bpkb
    nomor_polisi = fields.Text(string="Nomor Polisi")
    merek = fields.Text(string="Merek")
    type_ = fields.Text(string="Type")
    jenis = fields.Text(string="Jenis")
    isi_silinder = fields.Text(string="Isi Silinder")
    warna = fields.Text(string="Warna")
    no_rangka = fields.Text(string="No Rangka/ NIK")
    nomor_mesin = fields.Text(string="Nomor Mesin")
    bahan_bakar = fields.Text(string="Bahan Bakar")
    no_sertifikat = fields.Text(string="No Sertifikat Uji Type")
    no_uji_berkala = fields.Text(string="No Uji Berkala")

    jumlah_sumbu = fields.Integer(string="Jumlah Sumbu")
    jumlah_roda = fields.Integer(string="Jumlah Roda")
    pada_tanggal = fields.Datetime(string="Pada Tanggal")

    tp= fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'Tahun Pembuatan')
    tpera= fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'Tahun Perakitan')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('stop', 'Stopped'),
        
        ], string='Dikeluarkan di', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    model= fields.Selection([
        ('mb', 'Minibus'),
        ('mob','Mobil'),
        ('kereta,','Kereta'),
        ('truk)','Truk'),
        ],
        string ='Model')

    def confirm(self):
        self.write({'state':'active'})
        
    def stop(self):
        self.write({'state':'stop'})
        
    def reset_to_draft(self):
        self.write({'state':'draft'})